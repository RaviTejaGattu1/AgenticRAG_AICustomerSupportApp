# 🤖✨ AI Customer Support Agent 🚀🌌

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-🐇-orange)
![Cohere](https://img.shields.io/badge/Cohere-API-9cf)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-🚀%20Ready%20to%20Deploy-purple)

A **Flask-based chatbot** powered by **RAG (Retrieval-Augmented Generation)** for customer support, featuring multilingual magic 🌍, dynamic FAQ uploads 📄, query analytics 📊, and ticket escalation 🚨 via **RabbitMQ** 🐇. The UI rocks a sleek, cosmic dark theme with sparkling animations 🌠.

---

## 🌟 Features

- 💬 **RAG Chatbot:** Answers queries using **FAISS** + **Cohere’s free API**.
- 🌍 **Multilingual:** Supports **English**, **Spanish**, and **French** via Google Translator.
- 📄 **Dynamic FAQs:** Upload new `faq.txt` files to update responses instantly.
- 📊 **Analytics Sidebar:** Tracks query frequency live.
- 🚨 **Escalation System:** Routes complex queries to **RabbitMQ** and logs them in `tickets.json`.
- 🎨 **Cosmic UI:** Dark gradient background, neon chat bubbles, and sparkly animations ✨.

---

## 🛠️ Prerequisites

- 🐍 Python `3.8+`
- 🐇 RabbitMQ
- 💻 macOS/Linux (tested on macOS)

---

## ⚙️ Setup

### 📥 Clone the Repository:

```
git clone <your-repo-url>
cd ai-customer-support-agent
```
🐍 Create Virtual Environment:
```
python3 -m venv venv
source venv/bin/activate
```
📦 Install Dependencies:
```
pip install cohere==4.50 flask==2.3.3 langchain-community==0.2.0 langchain-huggingface==0.0.3 langgraph==0.2.0 faiss-cpu==1.8.0 deep-translator==1.11.4 pika==1.3.2 sentence-transformers==2.6.1 httpx==0.23.0 langchain-core==0.2.0
🔑 Configure API Key:
Sign up at 👉 https://dashboard.cohere.ai/, grab your free API key.
```

In app.py, replace:

```
Edit
co = cohere.Client("your-cohere-api-key")
with your actual API key.

🗝️ Set Secret Key:
bash
Copy
Edit
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
Replace the secret key in app.py:

python
Copy
Edit
app.secret_key = "your-new-generated-key"
🐇 Start RabbitMQ:
bash
Copy
Edit
rabbitmq-server
🚀 Run the App:
bash
Copy
Edit
export TOKENIZERS_PARALLELISM=false
python3 app.py
Then open:
👉 http://127.0.0.1:5000/

🕹️ Usage
💬 Chat: Enter customer queries like “How do I track my order?”.

🌍 Language Toggle: Choose between English, Spanish, and French.

📄 FAQ Upload: Upload a new faq.txt file to refresh FAQs instantly.

🧹 Clear Chat: Reset conversation history.

📊 Query Analytics: See live query counts in the sidebar.

🚨 Escalation: Complex queries get routed to RabbitMQ and logged into tickets.json.

📁 Project Structure
📄 File	📌 Description
app.py	Flask app integrating RAG, Cohere, and RabbitMQ.
templates/index.html	Chat interface with debug tools.
static/style.css	Cosmic UI styling with sparkles ✨
faq.txt	Sample FAQs database 📖
tickets.json	Logs for escalated queries 🚨
query_counts.json	JSON analytics for query frequency 📊

🛠️ Troubleshooting
🖥️ Chat not displaying?

Check debug section in UI, terminal logs, and browser DevTools (F12).

🔑 Cohere API errors?

Double-check your API key at 👉 https://dashboard.cohere.ai/

🐇 RabbitMQ issues?

Ensure it's running:

bash
Copy
Edit
rabbitmqctl status
📜 License
MIT License © 2025 👾✨

🎉 Done!
