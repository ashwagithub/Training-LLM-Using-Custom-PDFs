# 🧠 Training LLM Using Custom PDFs

This project allows users to **chat with their PDF documents** using a Large Language Model (LLM) like OpenAI’s GPT.  
It extracts text from uploaded PDFs, chunks the content, stores it as vectors, and retrieves relevant answers using LangChain and FAISS.

---

## 📸 Demo Screenshot

> 💡 Replace this image with your own UI/chat screenshot.

<p align="center">
  <img src="assets/main.png" width="600" alt="Project Screenshot" />
</p>

---

## 🔧 Features

- 📄 Extracts text from PDF files
- ✂️ Chunks text into manageable pieces
- 📊 Creates embeddings using OpenAI API
- 🧠 Stores and retrieves data with FAISS vector database
- 💬 Answers questions using LLM (via LangChain)
- 🖥️ Simple interface with Streamlit

---

## ⚙️ Technologies Used

- Python
- PyPDF2
- LangChain
- FAISS
- OpenAI API
- Streamlit

---

## 🛠️ How to Run

```bash
# Clone the repository
git clone https://github.com/your-username/llm-custom-pdf.git
cd llm-custom-pdf

# Create and activate a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Run the Streamlit app
streamlit run main.py
