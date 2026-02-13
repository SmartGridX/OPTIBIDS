# pipeline.py
from typing import List
import json
from sqlmodel import select

from .db import get_session
from .models import Tender, Requirement, SKU, Match, Pricing
from . import ai_agent, matcher, pricing as pricing_mod, consolidator

def run_pipeline(tender_id: int) -> None:
    # ------------------ LOAD TENDER ------------------
    with get_session() as session:
        tender = session.get(Tender, tender_id)
        if tender is None:
            print("Tender not found:", tender_id)
            return

        tender.status = "extracting"
        session.commit()

    # ------------------ STEP 1: Extract Requirements ------------------
    extracted = ai_agent.extract_requirements_from_text(
        tender.raw_text or tender.description
    )

    requirements = extracted.get("requirements", [])
    confidence = float(extracted.get("confidence", 0.9))

    with get_session() as session:
        session.add(
            Requirement(
                tender_id=tender_id,
                req_json=json.dumps(requirements),
                confidence=confidence,
            )
        )
        session.commit()

    # ------------------ STEP 2: Build SKU Index ------------------
    with get_session() as session:
        skus = session.exec(select(SKU)).all()

    vectors: List[List[float]] = [
        ai_agent.embed_text(sku.description or "") for sku in skus
    ]

    try:
        matcher.build_index(vectors)
    except Exception as e:
        print("FAISS error:", e)

    # ------------------ STEP 3: Matching ------------------
    matches_for_pricing = []

    with get_session() as session:
        tender = session.get(Tender, tender_id)
        tender.status = "matching"
        session.commit()

        for r in requirements:
            qv = ai_agent.embed_text(str(r.get("text", "")))
            ids, scores = matcher.search_index(qv, top_k=3)

            for idx, score in zip(ids, scores):
                if idx < len(skus):
                    sku = skus[idx]

                    session.add(
                        Match(
                            tender_id=tender_id,
                            sku_id=sku.id,
                            score=float(score),
                            explanation="auto",
                        )
                    )

                    matches_for_pricing.append({
                        "sku_code": sku.sku_code,
                        "price_base": sku.price_base,
                        "quantity": r.get("quantity", 1),
                    })

        session.commit()

    # ------------------ STEP 4: Pricing ------------------
    pricing_out = pricing_mod.compute_pricing(matches_for_pricing)

    with get_session() as session:
        tender = session.get(Tender, tender_id)
        tender.status = "pricing"

        session.add(
            Pricing(
                tender_id=tender_id,
                line_items=json.dumps(pricing_out["line_items"]),
                total_amount=float(pricing_out["total"]),
                margin_percent=10.0,
            )
        )
        session.commit()

    # ------------------ STEP 5: Proposal ------------------
    consolidator.make_proposal(
        requirements,
        pricing_out,
        {
            "name": "System",
            "source": "auto_pipeline"
        }
    )

    with get_session() as session:
        tender = session.get(Tender, tender_id)
        tender.status = "completed"
        session.commit()
