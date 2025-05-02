from flask import Flask, request, render_template, session, jsonify
from langgraph.graph import StateGraph, END
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from deep_translator import GoogleTranslator
import cohere
import json
import pika
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)
app.secret_key = "a7b9c2d8e4f6g1h3i5j0k2l4m6n8o0p"  # Change this!

# Cohere Client (Free Tier)
co = cohere.Client(" <Insert your api>  ")  # Replace with your Cohere API key

# Translator
translator = GoogleTranslator(source='auto', target='es')

# RabbitMQ Setup
rabbitmq_connection = None
channel = None
try:
    rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = rabbitmq_connection.channel()
    channel.queue_declare(queue='tickets')
    logger.info("RabbitMQ connected successfully")
except pika.exceptions.AMQPConnectionError as e:
    logger.error(f"Failed to connect to RabbitMQ: {e}")
    logger.info("Continuing without RabbitMQ; escalations will be logged to tickets.json only")

# FAQ Loader
def load_faq(file_path):
    with open(file_path, "r") as f:
        content = f.read().strip().split("\n\n")
    return [Document(page_content=entry) for entry in content if "Q:" in entry and "A:" in entry]

# Initialize FAQ Store
faq_documents = load_faq("faq.txt")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(faq_documents, embeddings)

# Analytics Store
def load_analytics():
    try:
        with open("query_counts.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_analytics(counts):
    with open("query_counts.json", "w") as f:
        json.dump(counts, f, indent=2)

# State for LangGraph
class State(dict):
    query: str
    retrieved: str
    response: str
    escalate: bool
    language: str

def greet(state):
    state["response"] = "Hello! How can I assist you today?"
    return state

def retrieve(state):
    try:
        docs = vector_store.similarity_search_with_score(state["query"], k=1)
        doc, distance = docs[0] if docs else (None, float('inf'))
        if doc and distance < 1.0:
            state["retrieved"] = doc.page_content.split("A:")[1].strip()
        else:
            state["retrieved"] = "No info found."
    except Exception as e:
        logger.error(f"Error in retrieve: {e}")
        state["retrieved"] = "No info found."
    return state

def respond(state):
    counts = load_analytics()
    query_key = state["query"].lower()
    counts[query_key] = counts.get(query_key, 0) + 1
    save_analytics(counts)

    if "urgent" in state["query"].lower():
        state["response"] = "I don’t have specific info for urgent requests."
        state["escalate"] = True
    elif "No info found" not in state["retrieved"]:
        try:
            prompt = f"Based on: '{state['retrieved']}', answer: {state['query']}"
            response = co.generate(
                prompt=prompt,
                model="command",
                max_tokens=200,
                temperature=0.7
            )
            state["response"] = response.generations[0].text.strip()
            if state["language"] != "en":
                translator.target = state["language"]
                state["response"] = translator.translate(state["response"])
        except Exception as e:
            logger.error(f"Error in Cohere call: {e}")
            state["response"] = "Error processing your request. Please try again."
            state["escalate"] = True
    else:
        state["response"] = "I don’t have that information."
        state["escalate"] = True
    return state

def escalate_query(state):
    if state["escalate"]:
        state["response"] += "\nI’m sorry, I can’t assist further. Escalating to a human agent."
        ticket = {"query": state["query"], "timestamp": str(datetime.now())}
        if channel and rabbitmq_connection:
            try:
                channel.basic_publish(exchange='', routing_key='tickets', body=json.dumps(ticket))
                logger.info("Ticket published to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to publish to RabbitMQ: {e}")
        with open("tickets.json", "a") as f:
            json.dump(ticket, f)
            f.write("\n")
    return state

workflow = StateGraph(State)
workflow.add_node("greet", greet)
workflow.add_node("retrieve", retrieve)
workflow.add_node("respond", respond)
workflow.add_node("escalate_query", escalate_query)
workflow.set_entry_point("greet")
workflow.add_edge("greet", "retrieve")
workflow.add_edge("retrieve", "respond")
workflow.add_edge("respond", "escalate_query")
workflow.add_edge("escalate_query", END)
graph_app = workflow.compile()

# Routes
@app.route("/", methods=["GET", "POST"])
def home():
    if "chat_history" not in session:
        session["chat_history"] = ["<b>Agent:</b> Hello! How can I assist you today?"]
    if "language" not in session:
        session["language"] = "en"

    counts = load_analytics()
    logger.info(f"Current chat_history: {session['chat_history']}")
    if request.method == "POST":
        try:
            logger.info(f"POST request received: {request.form}")
            # Handle clear chat
            if "clear" in request.form:
                session["chat_history"] = ["<b>Agent:</b> Hello! How can I assist you today?"]
                logger.info("Chat history cleared")
            # Handle FAQ upload
            elif "faq_file" in request.files:
                file = request.files["faq_file"]
                if file.filename.endswith(".txt"):
                    file.save("faq.txt")
                    global vector_store, faq_documents
                    faq_documents = load_faq("faq.txt")
                    vector_store = FAISS.from_documents(faq_documents, embeddings)
                    session["chat_history"].append("<b>Agent:</b> FAQ updated successfully!")
                    logger.info("FAQ updated successfully")
            # Handle query and language
            else:
                query = request.form.get("query", "").strip()
                language = request.form.get("language", session["language"])
                if language:
                    session["language"] = language
                    logger.info(f"Language set to: {session['language']}")
                if query:
                    logger.info(f"Processing query: {query}")
                    state = {
                        "query": query,
                        "retrieved": "",
                        "response": "",
                        "escalate": False,
                        "language": session["language"]
                    }
                    try:
                        result = graph_app.invoke(state)
                        session["chat_history"].append(f"<b>You:</b> {query}")
                        session["chat_history"].append(f"<b>Agent:</b> {result['response']}")
                        logger.info(f"Chat history updated: {session['chat_history'][-2:]}")
                    except Exception as e:
                        logger.error(f"Error processing query: {e}")
                        session["chat_history"].append(f"<b>You:</b> {query}")
                        session["chat_history"].append("<b>Agent:</b> Sorry, an error occurred. Please try again.")
                        logger.info(f"Chat history updated with error message: {session['chat_history'][-2:]}")
                else:
                    logger.warning("No valid query provided in form data")
            session.modified = True
        except Exception as e:
            logger.error(f"Error in POST route: {e}")
            session["chat_history"].append("<b>Agent:</b> An error occurred while processing your request.")
            session.modified = True
    logger.info(f"Rendering with chat_history: {session['chat_history']}")
    return render_template("index.html", chat_history=session["chat_history"], counts=counts, language=session["language"])

@app.route("/analytics", methods=["GET"])
def analytics():
    counts = load_analytics()
    return jsonify(counts)

if __name__ == "__main__":
    app.run(debug=True)