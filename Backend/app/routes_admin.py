from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlmodel import select
from typing import Optional
import os, uuid, json

from .db import get_session
from .auth_helpers import get_current_user
from .models import Tender, User, Application
from .pipeline import run_pipeline
from . import ai_agent

router = APIRouter()
UPLOAD_DIR = "/app/out"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------
# AUTH
# -------------------------------------------------
def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin only")
    return user

# -------------------------------------------------
# CREATE TENDER
# -------------------------------------------------
@router.post("/tenders")
async def create_tender(
    title: str = Form(...),
    description: str = Form(...),
    published: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    admin: User = Depends(require_admin),
):
    files = []

    if file:
        fname = f"{uuid.uuid4()}_{file.filename}"
        with open(os.path.join(UPLOAD_DIR, fname), "wb") as f:
            f.write(await file.read())
        files.append(fname)

    with get_session() as session:
        tender = Tender(
            title=title,
            description=description,
            raw_text=description,
            status="public" if published else "draft",
            files=json.dumps(files),
        )
        session.add(tender)
        session.commit()
        session.refresh(tender)

        return {"id": tender.id}

# -------------------------------------------------
# LIST TENDERS
# -------------------------------------------------
@router.get("/tenders")
def admin_list_tenders(admin: User = Depends(require_admin)):
    with get_session() as session:
        tenders = session.exec(
            select(Tender).where(Tender.status == "public")
        ).all()

        out = []
        for t in tenders:
            count = session.exec(
                select(Application).where(Application.tender_id == t.id)
            ).all()

            out.append({
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "applicant_count": len(count),
                "files": json.loads(t.files) if t.files else []
            })

        return out

# -------------------------------------------------
# LIST APPLICATIONS
# -------------------------------------------------
@router.get("/applications")
def admin_list_applications(admin: User = Depends(require_admin)):
    with get_session() as session:
        apps = session.exec(select(Application)).all()
        users = {u.id: u for u in session.exec(select(User)).all()}
        tenders = {t.id: t for t in session.exec(select(Tender)).all()}

        return [
            {
                "id": a.id,
                "user_email": users.get(a.user_id).email if a.user_id in users else "Unknown",
                "tender_title": tenders.get(a.tender_id).title if a.tender_id in tenders else "Unknown",
                "status": a.status or "submitted",
            }
            for a in apps
        ]

# -------------------------------------------------
# GET SINGLE APPLICATION
# -------------------------------------------------
@router.get("/applications/{application_id}")
def get_application(application_id: int, admin: User = Depends(require_admin)):
    with get_session() as session:
        app = session.get(Application, application_id)
        if not app:
            raise HTTPException(404, "Application not found")

        tender = session.get(Tender, app.tender_id)
        user = session.get(User, app.user_id)

        return {
            "id": app.id,
            "tender_title": tender.title if tender else "Unknown",
            "user_email": user.email if user else "Unknown",
            "applicant_text": app.applicant_text,
            "status": app.status,
        }

# -------------------------------------------------
# AI SUMMARY
# -------------------------------------------------
@router.post("/tenders/{tender_id}/summary")
def summarize_tender(tender_id: int, admin: User = Depends(require_admin)):
    with get_session() as session:
        tender = session.get(Tender, tender_id)
        if not tender:
            raise HTTPException(404, "Tender not found")

        apps = session.exec(
            select(Application, User)
            .where(Application.tender_id == tender_id)
            .where(Application.user_id == User.id)
        ).all()

        if not apps:
            return {"error": "No applications to summarize"}

        payload = [
            {
                "application_id": app.id,
                "email": user.email,
                "text": app.applicant_text,
            }
            for app, user in apps
        ]

    # AI OUTSIDE DB
    summary = ai_agent.build_user_summary(payload)

    with get_session() as session:
        tender = session.get(Tender, tender_id)
        tender.summary_json = json.dumps(summary)
        session.commit()

    return summary

# -------------------------------------------------
# SEND OFFER
# -------------------------------------------------
@router.post("/applications/{application_id}/offer")
def send_offer(
    application_id: int,
    data: dict,
    admin: User = Depends(require_admin),
):
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        raise HTTPException(400, "Offer message required")

    with get_session() as session:
        app = session.get(Application, application_id)
        if not app:
            raise HTTPException(404, "Application not found")

        app.status = "offered"
        app.offer_json = json.dumps({"message": message})
        session.commit()

        return {
            "status": "offered",
            "application_id": application_id
        }
# ---------------------------
# ACCEPTED OFFERS (ADMIN)
# ---------------------------
@router.get("/accepted-offers")
def admin_accepted_offers(admin: User = Depends(require_admin)):
    with get_session() as session:
        rows = session.exec(
            select(Application, User, Tender)
            .where(Application.status == "accepted")
            .where(Application.user_id == User.id)
            .where(Application.tender_id == Tender.id)
        ).all()

        return [
            {
                "application_id": app.id,
                "applicant_email": user.email,
                "tender_title": tender.title,
                "offer": json.loads(app.offer_json) if app.offer_json else None,
                "status": app.status,
            }
            for app, user, tender in rows
        ]
