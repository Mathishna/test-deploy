from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Set this in your Render environment

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def summarize_text(text):
    client = openai.OpenAI()  # use latest OpenAI SDK
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        if pdf_file:
            pdf_path = os.path.join("/tmp", "uploaded.pdf")  # ✅ Required for Render
            pdf_file.save(pdf_path)
            raw_text = extract_text_from_pdf(pdf_path)
            try:
                summary = summarize_text(raw_text)
            except Exception as e:
                return f"<h1>Error summarizing:</h1><pre>{e}</pre>"
            return f"<h1>Deal Summary:</h1><pre>{summary}</pre>"
    return render_template("index.html")
