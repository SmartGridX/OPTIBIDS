# backend/app/ai_agent.py

import os
import requests
import json
import hashlib
from typing import List, Dict

# Works inside Docker (service name = "ollama") and locally (localhost)
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_GENERATE = f"{OLLAMA_BASE}/api/generate"
MODEL = "phi3:mini"

def extract_requirements_from_text(text: str) -> Dict:
    prompt = f"""
You are an information extraction system.

Extract clear, atomic requirements from the following tender.

Return ONLY valid JSON in this exact format (no explanation, no markdown):

{{
  "requirements": [
    {{"text": "requirement description", "quantity": 1}}
  ],
  "confidence": 0.9
}}

Tender text:
{text}
"""

    r = None  # ✅ ensure r is always defined

    try:
        r = requests.post(
            OLLAMA_GENERATE,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        r.raise_for_status()

        raw = r.json().get("response", "").strip()
        if not raw:
            raise ValueError("Empty response from Ollama")

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("No JSON found in model output")

        data = json.loads(raw[start:end])

        if "requirements" not in data:
            raise ValueError("Missing 'requirements' key")

        return data

    except Exception as e:
        print("❌ Requirement extraction failed")
        print("Reason:", e)

        if r is not None:
            print("Raw Ollama output:", r.text)
        else:
            print("Raw Ollama output: request not sent")

        return {
            "requirements": [],
            "confidence": 0.0
        }

def generate_proposal_text(
    requirements: Dict,
    applicant_info: Dict,
    pricing: Dict
) -> str:
    """
    Generate proposal text (optional helper)
    """

    prompt = f"""
Create a professional proposal based on:

Requirements:
{requirements}

Applicant:
{applicant_info}

Pricing:
{pricing}
"""

    try:
        r = requests.post(
            OLLAMA_GENERATE,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        r.raise_for_status()

        return r.json().get("response", "Draft proposal unavailable")

    except Exception as e:
        print("❌ Proposal generation failed:", e)
        return "Draft proposal unavailable"


def embed_text(text: str) -> List[float]:
    """
    Deterministic lightweight embedding (mock)
    Safe for FAISS testing
    """

    h = hashlib.md5(text.encode()).digest()
    return [b / 255 for b in h]

def build_user_summary(applications: list[dict]) -> dict:
    """
    applications = [
      {
        "application_id": int,
        "email": str,
        "text": str
      }
    ]
    """

    # ---------------------------
    # Build structured input
    # ---------------------------
    joined = "\n\n".join(
        f"""
Application ID: {a['application_id']}
Email: {a['email']}
Proposal:
{a['text']}
"""
        for a in applications
    )

    # ---------------------------
    # STRICT JSON PROMPT
    # ---------------------------
    prompt = f"""
You are a professional RFP evaluation system.

Analyze ALL applications below.

Your tasks:
1. Extract proposed PRICE if mentioned.
2. Infer strengths and weaknesses.
3. Choose the BEST application overall.
4. Assign a SKU (short code) for each proposal.

Return ONLY valid JSON in EXACTLY this format:

{{
  "best_application": {{
    "application_id": number,
    "email": string,
    "price": string,
    "sku": string,
    "verdict": string,
    "brief": string
  }},
  "comparison": [
    {{
      "application_id": number,
      "email": string,
      "price": string,
      "strengths": [string],
      "weaknesses": [string]
    }}
  ]
}}

Rules:
- Do NOT include explanations outside JSON
- If price is missing, infer a reasonable estimate
- Be concise and professional

Applications:
{joined}
"""

    # ---------------------------
    # Call Ollama
    # ---------------------------
    r = requests.post(
        OLLAMA_GENERATE,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    r.raise_for_status()

    raw = r.json().get("response", "").strip()

    # ---------------------------
    # SAFE JSON EXTRACTION
    # ---------------------------
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
    except Exception as e:
        raise RuntimeError(
            f"AI returned invalid JSON.\nRaw output:\n{raw}"
        ) from e

    return parsed