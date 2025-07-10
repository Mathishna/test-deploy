import os
from flask import Flask, request, render_template
import fitz  # PyMuPDF
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def summarize_text(raw_text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a real estate investment analyst. Write polished, full-length real estate deal summaries in a professional tone. "
                    "Use the following structure with proper markdown-style headers and bullet points where appropriate:\n"
                    "\n"
                    "**Executive Summary**\n"
                    "**Property Overview**\n"
                    "**Tenant / Lease Summary**\n"
                    "**Ownership**\n"
                    "**Capital Improvements**\n"
                    "**Pricing Guidance**\n"
                    "\n"
                    "Follow this structure even if some sections are not applicable. Present the content as if for a pitch book or IC memo."
                )
            },
            {"role": "user", "content": raw_text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        pdf_path = os.path.join("/tmp", "uploaded.pdf")
        pdf_file.save(pdf_path)

        try:
            raw_text = extract_text_from_pdf(pdf_path)
            summary = summarize_text(raw_text)
        except Exception as e:
            return f"<h1>Error summarizing:</h1><pre>{e}</pre>"

        return render_template("result.html", summary=summary)

    return render_template("index.html")
