// File: full_app

// FRONTEND (React + Tailwind CSS)
// File: frontend/src/App.tsx
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud } from "lucide-react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/upload", formData);
      setSummary(response.data.summary);
    } catch (error) {
      console.error("Upload failed", error);
      setSummary("Error: Unable to generate summary.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <Card className="w-full max-w-4xl shadow-lg">
        <CardContent className="p-6">
          <h1 className="text-3xl font-bold mb-6 text-center">Deal Summary Generator</h1>
          <div className="flex flex-col items-center mb-4">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="mb-4"
            />
            <Button onClick={handleUpload} disabled={!file || loading}>
              <UploadCloud className="mr-2 h-4 w-4" />
              {loading ? "Processing..." : "Upload PDF"}
            </Button>
          </div>
          {summary && (
            <div className="mt-6 bg-white p-4 rounded border border-gray-300">
              <h2 className="text-xl font-semibold mb-4">Generated Deal Summary</h2>
              <article className="prose prose-sm text-gray-900 max-w-none whitespace-pre-wrap">{summary}</article>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// BACKEND (FastAPI)
// File: backend/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class SummaryResponse(BaseModel):
    summary: str

TEMPLATE_INSTRUCTIONS = """
You are a professional real estate AI that creates investment-facing deal summaries ONLY for office and industrial properties.
Your output must follow this EXACT structure and tone:

**[Property Name]** ("The Property") is a [Class A/B] [office/industrial] asset totaling [RSF] located in [City/Market]. Built in [Year], the Property is currently [XX]% leased to [#] tenants with a WALT of [X.X years]. Notable tenants include [list notable tenants]. The asset features [highlight amenities], and offers [summary of investment value proposition].

---

### Property Overview
- **Address:** [Street, City, State]
- **Asset Type:** [Office / Industrial]
- **Year Built:** [Year]
- **Total Rentable SF:** [RSF]
- **Stories:** [# Above / Below if relevant]
- **Occupancy:** [XX.X%]
- **Zoning:** [Zoning Type]
- **Parking:** [Spaces and Ratio if available]
- **Certifications:** [LEED, Energy Star, etc. if any]

### Tenant / Lease Summary
- **Major Tenants & Expirations:**
  - **Tenant 1** | RSF: [X] | LXD: [mm/dd/yyyy] | Annual Rent: [$X] | Rent PSF: [$X.XX]
  - **Tenant 2** | RSF: [X] | ...
- **WALT:** [X.X Years]
- **Annual Rental Revenue:** [$X]
- **Rent Type:** [NNN / FSG / MTM]
- **NOI:** [$X] (if available)
- **Renewal Options:** [List options or state 'None']

### Ownership
- **Current Ownership:** [Entity or Owner Name]
- **Loan Status (if applicable):** [Performing / Non-Performing]
- **Unpaid Principal Balance:** [$X] (if applicable)
- **Maturity Date:** [mm/yyyy] (if applicable)
- **Interest Rate:** [X.XX%]

### Pricing Guidance
- TBD (or $X | $X PSF | X.X% cap rate)

ONLY return content in that format. Do not add sections, bullet points, labels, or commentary outside of this.
"""

@app.post("/upload", response_model=SummaryResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": TEMPLATE_INSTRUCTIONS},
                {"role": "user", "content": text[:20000]}
            ],
            temperature=0.2,
        )

        summary_text = response.choices[0].message.content
        return {"summary": summary_text.strip()}

    except Exception as e:
        return {"summary": f"Error: {str(e)}"}
