# 🧠 Training LLM Using Custom PDFs

A smart assistant that lets you **chat with your PDF files** using the power of Large Language Models (LLMs).  
Built with **LangChain**, **OpenAI**, **FAISS**, and **Streamlit**, this project enables natural language question-answering from any uploaded PDF document.

---

## 📄 Project Overview

This mini-project is designed to demonstrate how to interact with custom PDF documents using a conversational interface powered by a **Large Language Model** (LLM). It solves the problem of manually searching through lengthy PDF documents by allowing users to **ask questions and receive instant answers**, as if the AI had read the documents.

The core approach uses **Retrieval-Augmented Generation (RAG)**:
- Extracts text from uploaded PDFs
- Splits the text into smaller, context-preserving chunks
- Converts text chunks into vectors (embeddings)
- Stores them in a vector database (FAISS)
- Uses OpenAI GPT or Hugging Face models to generate intelligent, contextual answers

---

### 🌟 Why It Matters

Instead of reading pages manually, users can ask:
- *"What’s the conclusion of the research?"*
- *"Summarize the legal clause in section 4."*
- *"List key findings of this report."*

This saves time and improves productivity.

---

### 🌍 Use Cases

- 📚 Academic research assistant
- 🏢 Business report analyzer
- 🧑‍🏫 Educational tool
- ⚖️ Legal and policy document search
- 🩺 Medical literature review

---

## 📸 Chat_With_PDFs

> 💡 User Interface.

<p align="center">
  <img src="assets/main.png" width="600" alt="Chatbot Demo Screenshot" />
</p>

---

## 🔧 Features

- 📄 Upload multiple PDF files
- ✂️ Split and chunk text intelligently
- 🔍 Create semantic embeddings
- 🧠 Search with vector similarity (FAISS)
- 💬 Get answers from GPT/LLM via LangChain
- 🖥️ Simple interface with Streamlit

---

## ⚙️ Technologies Used

| Technology     | Purpose                          |
|----------------|----------------------------------|
| Python         | Main programming language        |
| PyPDF2         | PDF text extraction              |
| LangChain      | LLM + memory + retrieval chain   |
| FAISS          | Vector storage and similarity    |
| OpenAI API     | Embedding + LLM response         |
| Streamlit      | Frontend web interface           |

---

## 🛠️ How to Run

```bash
# 1. Clone the repository
git clone https://github.com/your-username/llm-custom-pdf.git
cd llm-custom-pdf

# 2. Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate for Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run main.py
