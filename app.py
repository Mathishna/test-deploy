from flask import Flask, request, render_template, redirect, url_for
import fitz  # PyMuPDF

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["pdf"]
        if uploaded_file.filename != "":
            pdf_data = uploaded_file.read()
            text = extract_text_from_pdf(pdf_data)
            # Here, you could summarize with OpenAI (optional)
            return render_template("result.html", text=text)
    return render_template("index.html")

def extract_text_from_pdf(pdf_data):
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

