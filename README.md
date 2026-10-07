# 🤖 RAG Knowledge Assistant

A **Retrieval-Augmented Generation (RAG) based Knowledge Assistant** built using **Python, Flask, ChromaDB, LangChain, and Gemini AI**.

The application allows users to upload **PDF or TXT documents**, process their content into a searchable knowledge base, and ask questions about the uploaded documents. The system retrieves relevant information from the documents and generates answers using an AI language model.

---

## 📌 Project Overview

The **RAG Knowledge Assistant** is designed to make document-based information retrieval easier and more interactive.

Instead of manually searching through large documents, users can:

1. Upload a PDF or TXT document.
2. Extract and process the document content.
3. Store document information as searchable chunks.
4. Ask questions in natural language.
5. Retrieve relevant information from the knowledge base.
6. Generate an AI-powered answer.
7. View the sources used to generate the answer.
8. Clear the existing knowledge base and upload new documents.

This project demonstrates how **Retrieval-Augmented Generation (RAG)** can be used to build an intelligent document question-answering system.

---

## ✨ Features

### 📄 Document Upload

* Upload PDF and TXT files.
* Secure file naming using `secure_filename()`.
* Automatic document processing.
* Uploaded files are stored in the `uploads` directory.

### 🧠 RAG-Based Question Answering

* Ask questions about uploaded documents.
* Relevant document chunks are retrieved from the knowledge base.
* AI generates an answer based on the retrieved information.

### 🔎 Source Retrieval

The system provides the relevant document sources used while generating an answer, making the response more transparent.

### 🗄️ Vector Database

Document chunks are converted into embeddings and stored in a vector database for efficient similarity-based searching.

### 🧹 Clear Knowledge Base

Users can clear the existing knowledge base and uploaded documents using the **Clear Data** functionality.

### 📊 Knowledge Base Statistics

The application displays statistics about the currently stored knowledge base.

### 🌐 Web Interface

A simple Flask-based web interface allows users to upload documents and interact with the RAG assistant through a browser.

---

## 🏗️ System Architecture

```text
                 ┌─────────────────────┐
                 │       User          │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Flask Web App    │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ Document Upload │   │ Ask Question    │
        └────────┬────────┘   └────────┬────────┘
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ Document        │   │ Query Processing│
        │ Processing      │   └────────┬────────┘
        └────────┬────────┘            │
                 ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ Text Splitting  │   │ Vector Search   │
        └────────┬────────┘   └────────┬────────┘
                 │                     │
                 ▼                     ▼
        ┌─────────────────────────────────────┐
        │          ChromaDB Vector DB         │
        └──────────────────┬──────────────────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │    Gemini AI / LLM  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Generated Answer   │
                 └─────────────────────┘
```

---

## 🛠️ Technologies Used

| Technology        | Purpose                              |
| ----------------- | ------------------------------------ |
| **Python**        | Core programming language            |
| **Flask**         | Web application framework            |
| **LangChain**     | RAG pipeline and document processing |
| **ChromaDB**      | Vector database                      |
| **Gemini AI**     | Embeddings / AI response generation  |
| **PyPDF**         | PDF document extraction              |
| **HTML/CSS**      | Frontend interface                   |
| **Werkzeug**      | Secure file handling                 |
| **python-dotenv** | Environment variable management      |

---

## 📂 Project Structure

```text
rag-assistant/
│
├── app.py
├── rag_engine.py
├── requirements.txt
├── .env
├── .gitignore
│
├── templates/
│   ├── index.html
│   └── result.html
│
├── static/
│   └── style.css
│
├── uploads/
│
├── knowledge_base/
│
└── README.md
```

### File Description

**`app.py`**

Main Flask application. It handles:

* Home page
* Document uploads
* Question submission
* Knowledge-base statistics
* Clearing uploaded documents
* Running the Flask server

**`rag_engine.py`**

Contains the main RAG functionality including:

* Document loading
* Text splitting
* Embedding generation
* Vector database management
* Document retrieval
* AI-generated responses

**`templates/index.html`**

Main user interface for uploading documents and asking questions.

**`templates/result.html`**

Displays the user's question, generated answer, sources, and knowledge-base information.

**`static/style.css`**

Contains the styling for the web application.

**`uploads/**`

Stores uploaded PDF and TXT documents.

**`knowledge_base/**`

Stores the local vector database used for document retrieval.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Move into the project directory:

```bash
cd rag-assistant
```

---

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Gemini API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

⚠️ **Do not upload your `.env` file to GitHub.**

Add the following to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
uploads/*
knowledge_base/*
*.pyc
```

---

## ▶️ Running the Application

Start the Flask application:

```bash
python app.py
```

You should see:

```text
🚀 Starting RAG Knowledge Assistant...
🌐 Open http://localhost:5000 in your browser
```

Open your browser and visit:

```text
http://localhost:5000
```

---

## 📄 How to Use

### Step 1 — Upload a Document

Upload a:

* `.pdf`
* `.txt`

document through the web interface.

### Step 2 — Process the Document

The RAG engine processes the document and stores its content in the vector database.

### Step 3 — Ask a Question

Enter a question related to the uploaded document.

For example:

```text
What is the main purpose of this document?
```

or:

```text
Explain the methodology described in the document.
```

### Step 4 — Get the Answer

The system retrieves relevant document chunks and generates an AI-powered response.

### Step 5 — View Sources

The application also displays the document sources used to answer the question.

### Step 6 — Clear Data

Use the **Clear Data** option when you want to remove the current knowledge base and uploaded documents.

---

## 🔄 RAG Workflow

The project follows the following workflow:

```text
Document Upload
       ↓
Document Loading
       ↓
Text Extraction
       ↓
Text Chunking
       ↓
Embedding Generation
       ↓
ChromaDB Vector Storage
       ↓
User Question
       ↓
Question Embedding
       ↓
Similarity Search
       ↓
Relevant Document Chunks
       ↓
Gemini AI
       ↓
Generated Answer
       ↓
Answer + Sources
```

---

## 🔐 Security

The application uses `secure_filename()` from Werkzeug to safely handle uploaded filenames.

API credentials should be stored in environment variables instead of directly inside the source code.

Example:

```env
GEMINI_API_KEY=your_api_key
```

The `.env` file should **never be committed to GitHub**.

---

## 🚀 Future Improvements

The project can be extended with:

* [ ] Multiple document support
* [ ] DOCX document support
* [ ] Image/OCR document processing
* [ ] Chat history
* [ ] User authentication
* [ ] Multiple knowledge bases
* [ ] Document deletion
* [ ] Better source citations
* [ ] Streaming AI responses
* [ ] Voice-based questions
* [ ] Cloud deployment
* [ ] PostgreSQL/MongoDB integration
* [ ] Advanced RAG evaluation
* [ ] Admin dashboard

---

## 🎯 Applications

This project can be used for:

* 📚 Academic document analysis
* 📖 Research paper question answering
* 🏢 Company knowledge bases
* 📑 Legal document analysis
* 🎓 Educational assistants
* 📋 Technical documentation
* 💼 Resume/CV analysis
* 🧑‍💻 Developer documentation assistants

---

## 📈 Project Objective

The primary objective of this project is to develop an intelligent **document-based question-answering system** that combines information retrieval with generative AI.

The system reduces the time required to search large documents manually and provides users with relevant, context-aware answers based on their uploaded documents.

---

## 👨‍💻 Author

**Shubham Pratap**

MCA – Data Science & Artificial Intelligence

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

## 📜 License

This project is intended for educational and research purposes.
