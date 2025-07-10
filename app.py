from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF
from openai import OpenAI

app = Flask(__name__)

# Make sure the OPENAI_API_KEY is set in your environment (e.g., Render's dashboard)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def summarize_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a real estate analyst. Summarize this real estate offering memo with bullet points including asset type, location, tenants, rent roll, lease details, pricing, and investment highlights."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<h1>Error summarizing:</h1><pre>{e}</pre>"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        if pdf_file:
            pdf_path = os.path.join("/tmp", "uploaded.pdf")  # ✅ Write to /tmp on Render
            pdf_file.save(pdf_path)
            raw_text = extract_text_from_pdf(pdf_path)
            summary = summarize_text(raw_text)
            return f"<h1>Deal Summary:</h1><pre>{summary}</pre>"
    return render_template("index.html")
