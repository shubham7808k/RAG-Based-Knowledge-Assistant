import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from rag_engine import RAGEngine
app = Flask(__name__)
app.secret_key = "my-rag-secret-key-123"

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("./knowledge_base", exist_ok=True)

# Initialize RAG Engine
rag = RAGEngine()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---- HOME PAGE ----
@app.route("/")
def index():
    stats = rag.get_stats()
    return render_template("index.html", stats=stats)


# ---- UPLOAD DOCUMENT ----
@app.route("/upload", methods=["POST"])
def upload_document():

    print("\n========== UPLOAD DEBUG ==========")
    print("Request method:", request.method)
    print("Files received:", request.files)

    if "document" not in request.files:
        print("ERROR: document field NOT received")
        flash("No file was received by Flask", "error")
        return redirect(url_for("index"))

    file = request.files["document"]

    print("Filename:", file.filename)

    if file.filename == "":
        print("ERROR: filename is empty")
        flash("No file selected", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        print("ERROR: unsupported file type")
        flash("Only PDF and TXT files are allowed", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    print("Saving file to:", file_path)

    try:
        file.save(file_path)

        print("File saved successfully")

        result = rag.ingest_document(file_path)

        print("RAG result:", result)

        if result["status"] == "success":
            flash(result["message"], "success")
        else:
            flash(result["message"], "error")

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        flash(f"Upload error: {str(e)}", "error")

    return redirect(url_for("index"))

# ---- ASK QUESTION ----
@app.route("/ask", methods=["POST"])
def ask_question():
    question = request.form.get("question", "").strip()

    if not question:
        flash("Please enter a question", "error")
        return redirect(url_for("index"))

    result = rag.ask(question)
    stats = rag.get_stats()

    return render_template(
        "result.html",
        question=result["query"],
        answer=result["answer"],
        sources=result["sources"],
        stats=stats,
    )


# ---- CLEAR DATA ----
@app.route("/clear", methods=["POST"])
def clear_data():
    rag.clear_all()

    for f in os.listdir(UPLOAD_FOLDER):
        fp = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(fp):
            os.remove(fp)

    flash("Knowledge base cleared", "success")
    return redirect(url_for("index"))


# ---- RUN ----
if __name__ == "__main__":
    print("\n🚀 Starting RAG Knowledge Assistant...")
    print("🌐 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)