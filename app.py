from flask import Flask, request, render_template
import os
import fitz  # PyMuPDF
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def summarize_text(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are a real estate investment analyst. Format the output strictly in this structure: \n\n"
                    "Intro Summary\n"
                    "\nProperty Overview\n"
                    "- Location\n"
                    "- Total RSF\n"
                    "- Year Built / Renovated\n"
                    "- Zoning\n"
                    "- Stories\n"
                    "- Parking\n"
                    "- Ceiling Heights\n"
                    "- Amenities\n"
                    "- Notable\n"
                    "\nTenant / Lease Summary\n"
                    "- Major Tenants with RSF, Lease Expiry Date, Rent PSF\n"
                    "- Total Occupancy\n"
                    "- WALT\n"
                    "- Annual Rental Revenue\n"
                    "- Rent Type\n"
                    "- Rent Bumps\n"
                    "- Renewal Options\n"
                    "\nOwnership\n"
                    "- Ownership Structure\n"
                    "- Capital Improvements\n"
                    "- Ownership History\n"
                    "\nPricing Guidance\n"
                    "- Include if available"
                )},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing:\n{e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files.get("pdf")
        if pdf_file:
            pdf_path = os.path.join("/tmp", "uploaded.pdf")
            pdf_file.save(pdf_path)
            raw_text = extract_text_from_pdf(pdf_path)
            summary = summarize_text(raw_text)
            return render_template("result.html", summary=summary)
    return render_template("index.html")
