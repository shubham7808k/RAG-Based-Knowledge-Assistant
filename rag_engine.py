import os
import shutil

from dotenv import load_dotenv
import google.generativeai as genai

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings


load_dotenv()


# ============================================================
# Gemini Embeddings
# ============================================================

class GeminiEmbeddings(Embeddings):

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        genai.configure(api_key=api_key)
        self.api_key = api_key

    def embed_documents(self, texts):
        embeddings = []

        for text in texts:
            if not text or not text.strip():
                continue

            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
            )

            embeddings.append(result["embedding"])

        return embeddings

    def embed_query(self, text):

        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
        )

        return result["embedding"]


# ============================================================
# RAG ENGINE
# ============================================================

class RAGEngine:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY missing from .env file!"
            )

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-3.5-flash"
        )

        self.embeddings = GeminiEmbeddings(
            api_key=api_key
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )

        self.vector_db = None

        self.persist_dir = "./knowledge_base"

        self.collection_name = "rag_collection"

        self.history = []

        os.makedirs(self.persist_dir, exist_ok=True)

        self._load_existing_db()


    # ========================================================
    # LOAD EXISTING DATABASE
    # ========================================================

    def _load_existing_db(self):

        try:

            if not os.path.exists(self.persist_dir):
                self.vector_db = None
                return

            db = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
            )

            count = db._collection.count()

            print(f"Existing Chroma chunks: {count}")

            if count > 0:
                self.vector_db = db
                print(
                    f"Loaded existing database with {count} chunks"
                )
            else:
                self.vector_db = None

        except Exception as e:

            print(
                f"Could not load existing database: {e}"
            )

            self.vector_db = None


    # ========================================================
    # INGEST DOCUMENT
    # ========================================================

    def ingest_document(self, file_path):

        try:

            print("\n========== RAG INGEST ==========")
            print(f"File: {file_path}")

            # ----------------------------------------------
            # Check file
            # ----------------------------------------------

            if not os.path.exists(file_path):

                return {
                    "status": "error",
                    "message": "Uploaded file does not exist."
                }

            ext = os.path.splitext(file_path)[1].lower()

            # ----------------------------------------------
            # Select loader
            # ----------------------------------------------

            if ext == ".pdf":

                loader = PyPDFLoader(file_path)

            elif ext == ".txt":

                loader = TextLoader(
                    file_path,
                    encoding="utf-8"
                )

            else:

                return {
                    "status": "error",
                    "message": "Only PDF and TXT files are allowed."
                }

            # ----------------------------------------------
            # Load document
            # ----------------------------------------------

            documents = loader.load()

            print(
                f"Loaded pages/documents: {len(documents)}"
            )

            if not documents:

                return {
                    "status": "error",
                    "message": "Document is empty."
                }

            # ----------------------------------------------
            # Split document
            # ----------------------------------------------

            chunks = self.splitter.split_documents(
                documents
            )

            print(
                f"Created chunks: {len(chunks)}"
            )

            # ----------------------------------------------
            # IMPORTANT
            # ----------------------------------------------

            if not chunks:

                return {
                    "status": "error",
                    "message": (
                        "No text could be extracted from "
                        "the uploaded document. "
                        "If this is a scanned PDF, "
                        "OCR may be required."
                    )
                }

            # Remove empty chunks
            valid_chunks = []

            for chunk in chunks:

                if (
                    chunk.page_content
                    and chunk.page_content.strip()
                ):
                    valid_chunks.append(chunk)

            chunks = valid_chunks

            print(
                f"Valid chunks: {len(chunks)}"
            )

            if not chunks:

                return {
                    "status": "error",
                    "message": (
                        "The document contains no readable text."
                    )
                }

            # ----------------------------------------------
            # Remove old Chroma database
            #
            # This avoids the empty-ID problem caused by
            # an old/corrupted collection.
            # ----------------------------------------------

            if os.path.exists(self.persist_dir):

                try:

                    shutil.rmtree(self.persist_dir)

                    print(
                        "Old Chroma database removed."
                    )

                except Exception as e:

                    print(
                        f"Could not remove old database: {e}"
                    )

            os.makedirs(
                self.persist_dir,
                exist_ok=True
            )

            # ----------------------------------------------
            # Create NEW Chroma database
            # ----------------------------------------------

            print(
                "Creating new Chroma database..."
            )

            self.vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_dir,
                collection_name=self.collection_name,
            )

            # ----------------------------------------------
            # Verify database
            # ----------------------------------------------

            count = self.vector_db._collection.count()

            print(
                f"Chroma database contains {count} chunks."
            )

            if count == 0:

                self.vector_db = None

                return {
                    "status": "error",
                    "message": (
                        "Document was processed, "
                        "but no chunks were stored in ChromaDB."
                    )
                }

            print("========== INGEST SUCCESS ==========\n")

            return {
                "status": "success",
                "message": (
                    f"Successfully processed "
                    f"{count} chunks from the document."
                ),
            }

        except Exception as e:

            print("\n========== INGEST ERROR ==========")
            print(str(e))
            print("=================================\n")

            return {
                "status": "error",
                "message": str(e),
            }


    # ========================================================
    # ASK QUESTION
    # ========================================================
    def ask(self, question):

        if not question or not question.strip():
            return {
                "answer": "Please enter a question.",
                "sources": [],
                "query": question,
            }

        # Load existing database if necessary
        if self.vector_db is None:
            self._load_existing_db()

        if self.vector_db is None:
            return {
                "answer": (
                    "No document has been uploaded yet. "
                    "Please upload a PDF or TXT document first."
                ),
                "sources": [],
                "query": question,
            }

        try:

            # Get all stored document chunks
            collection_data = self.vector_db.get()

            all_documents = collection_data.get(
                "documents", []
            )

            all_metadatas = collection_data.get(
                "metadatas", []
            )

            if not all_documents:
                return {
                    "answer": (
                        "The document was uploaded, "
                        "but no readable text was found."
                    ),
                    "sources": [],
                    "query": question,
                }

            print(
                f"Available document chunks: "
                f"{len(all_documents)}"
            )

            # Check question
            question_lower = question.lower()

            summary_keywords = [
                "what is this document",
                "what is the document",
                "about this document",
                "about the document",
                "summarize",
                "summary",
                "summarise",
                "main topic",
                "main topics",
                "overview",
                "important points",
                "key points",
                "give me information about the document",
                "information about the document",
            ]

            is_summary_question = any(
                keyword in question_lower
                for keyword in summary_keywords
            )

            # ------------------------------------------------
            # GENERAL DOCUMENT INFORMATION
            # ------------------------------------------------

            if is_summary_question:

                selected_documents = all_documents[:20]

                context = "\n\n".join(
                    selected_documents
                )

                sources = []

                for i, content in enumerate(
                    selected_documents
                ):

                    metadata = {}

                    if i < len(all_metadatas):
                        metadata = all_metadatas[i]

                    preview = content

                    if len(preview) > 200:
                        preview = preview[:200] + "..."

                    sources.append(
                        {
                            "content": preview,
                            "metadata": metadata,
                        }
                    )

            # ------------------------------------------------
            # NORMAL QUESTION
            # ------------------------------------------------

            else:



                docs = self.vector_db.similarity_search(
                    question,
                    k=8
                )

                if not docs:
                    return {
                        "answer": (
                            "No relevant information was found "
                            "in the uploaded document."
                        ),
                        "sources": [],
                        "query": question,
                    }

                # ------------------------------------------------
                # Remove duplicate / highly similar chunks
                # ------------------------------------------------

                unique_docs = []

                for doc in docs:

                    current_text = " ".join(
                        doc.page_content.lower().split()
                    )

                    is_duplicate = False

                    for existing_doc in unique_docs:

                        existing_text = " ".join(
                            existing_doc.page_content.lower().split()
                        )

                        current_words = set(
                            current_text.split()
                        )

                        existing_words = set(
                            existing_text.split()
                        )

                        if not current_words:
                            continue

                        overlap = (
                            len(current_words & existing_words)
                            / len(current_words)
                        )

                        # 70% or more similarity = duplicate
                        if overlap >= 0.70:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        unique_docs.append(doc)

                # Keep maximum 3 useful sources
                unique_docs = unique_docs[:3]

                # ------------------------------------------------
                # Create context for Gemini
                # ------------------------------------------------

                context = "\n\n".join(
                    [
                        doc.page_content
                        for doc in unique_docs
                    ]
                )

                # ------------------------------------------------
                # Create sources for UI
                # ------------------------------------------------

                sources = []

                for doc in unique_docs:

                    content = doc.page_content.strip()

                    if len(content) > 250:
                        content = content[:250] + "..."

                    sources.append(
                        {
                            "content": content,
                            "metadata": doc.metadata,
                        }
                    )        

            # ------------------------------------------------
            # Gemini Prompt
            # ------------------------------------------------

            prompt = f"""
You are an intelligent document assistant.

The user has uploaded a document.

Answer the user's question using ONLY
information contained in the document.

If the user asks what the document is about,
provide a clear overview.

If the user asks for a summary,
summarize the important information.

If the user asks for important points,
provide them as bullet points.

Do not invent information that is not
present in the document.

Document Context:
-------------------------
{context}
-------------------------

User Question:
{question}

Answer clearly and professionally.
"""

            # ------------------------------------------------
            # Generate answer
            # ------------------------------------------------

            try:

                response = self.model.generate_content(
                    prompt
                )

                answer = response.text

                return {
                    "answer": answer,
                    "sources": sources,
                    "query": question,
                }

            except Exception as e:

                return {
                    "answer": (
                        f"Error generating answer: {str(e)}"
                    ),
                    "sources": sources,
                    "query": question,
                }

        except Exception as e:

            print(
                f"RAG search error: {str(e)}"
            )

            return {
                "answer": (
                    f"Error reading the uploaded document: {str(e)}"
                ),
                "sources": [],
                "query": question,
            }
        # ========================================================
    # GET DATABASE STATS
    # ========================================================

    def get_stats(self):

        try:

            if self.vector_db is not None:

                count = self.vector_db._collection.count()

                return {
                    "total_chunks": count
                }

        except Exception as e:

            print(
                f"Error getting database stats: {e}"
            )

        return {
            "total_chunks": 0
        }


    # ========================================================
    # CLEAR DATABASE
    # ========================================================

    def clear_all(self):

        try:

            if os.path.exists(
                self.persist_dir
            ):

                shutil.rmtree(
                    self.persist_dir
                )

            os.makedirs(
                self.persist_dir,
                exist_ok=True
            )

            self.vector_db = None
            self.history = []

            print(
                "Knowledge base cleared."
            )

        except Exception as e:

            print(
                f"Error clearing database: {e}"
            )