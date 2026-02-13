import json
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from typing import cast

from .models import Application, Tender, User
from .db import get_session
from .auth_helpers import get_current_user, require_applicant

router = APIRouter(tags=["Applicant"])

# --------------------------------------------------
# SUBMIT APPLICATION
# --------------------------------------------------
@router.post("/submit_application")
def submit_application(data: dict, user: User = Depends(require_applicant)):
    if user.id is None:
        raise HTTPException(500, "Authenticated user has no ID")

    tender_id = data.get("tender_id")
    text = str(data.get("text", "")).strip()

    if not isinstance(tender_id, int):
        raise HTTPException(400, "tender_id must be an integer")

    if not text:
        raise HTTPException(400, "Application text cannot be empty")

    with get_session() as session:
        tender = session.get(Tender, tender_id)
        if tender is None:
            raise HTTPException(404, "Tender not found")

        if tender.status != "public":
            raise HTTPException(403, "Tender is not open for applications")

        existing = session.exec(
            select(Application)
            .where(Application.tender_id == tender_id)
            .where(Application.user_id == user.id)
        ).first()

        if existing:
            raise HTTPException(400, "You have already applied")

        app = Application(
            tender_id=tender_id,
            user_id=cast(int, user.id),
            applicant_text=text,
            status="submitted",
        )

        session.add(app)
        session.commit()
        session.refresh(app)

        return {
            "status": "submitted",
            "application_id": app.id,
        }

# --------------------------------------------------
# APPLICANT NOTIFICATIONS
# --------------------------------------------------
@router.get("/notifications")
def applicant_notifications(user: User = Depends(get_current_user)):
    if user.id is None:
        raise HTTPException(500, "Authenticated user has no ID")

    with get_session() as session:
        apps = session.exec(
            select(Application)
            .where(Application.user_id == user.id)
            .where(Application.status == "offered")
        ).all()

        return [
            {
                "application_id": a.id,
                "tender_id": a.tender_id,
                "offer": json.loads(a.offer_json) if a.offer_json else None,
            }
            for a in apps
        ]

# --------------------------------------------------
# ACCEPT / REJECT OFFER
# --------------------------------------------------
@router.post("/offer/{application_id}/respond")
def respond_to_offer(
    application_id: int,
    decision: str,
    user: User = Depends(require_applicant),
):
    if decision not in ("accept", "reject"):
        raise HTTPException(400, "Decision must be 'accept' or 'reject'")

    with get_session() as session:
        app = session.get(Application, application_id)

        if not app:
            raise HTTPException(404, "Application not found")

        if app.user_id != user.id:
            raise HTTPException(403, "Unauthorized")

        if app.status != "offered":
            raise HTTPException(400, "No active offer")

        app.status = "accepted" if decision == "accept" else "rejected"
        session.commit()

        return {
            "status": app.status,
            "application_id": application_id,
        }
# ---------------------------
# ACCEPTED OFFERS (APPLICANT)
# ---------------------------
@router.get("/accepted")
def applicant_accepted(user: User = Depends(require_applicant)):
    if user.id is None:
        raise HTTPException(500, "User has no ID")

    with get_session() as session:
        apps = session.exec(
            select(Application)
            .where(Application.user_id == user.id)
            .where(Application.status == "accepted")
        ).all()

        result = []
        for a in apps:
            tender = session.get(Tender, a.tender_id)

            result.append({
                "application_id": a.id,
                "tender_title": tender.title if tender else "Unknown",
                "offer": json.loads(a.offer_json) if a.offer_json else None,
                "status": a.status
            })

        return result


