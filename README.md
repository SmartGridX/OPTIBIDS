# OPTIBIDS — AI-Powered RFP & Tender Evaluation Platform

OPTIBIDS is a B2B AI-driven Request for Proposal (RFP) and Tender Management platform that automates:

- Tender publishing

- Vendor application submissions

- AI-based proposal analysis

- SKU-based pricing estimation

- Offer negotiation and acceptance tracking

The system is designed for enterprise procurement teams and vendors to collaborate efficiently using AI assistance.

---

### 🧠 Key Features
Admin (Buyer)

- Create and publish tenders

- Upload supporting documents

- View all vendor applications

- Generate AI summaries of proposals

- Compare applicants objectively

- Send offers to selected vendors

- Track accepted/rejected offers

- Applicant (Vendor)

- Browse public tenders

- Submit technical & pricing proposals

- Receive offers from admins

- Accept or reject offers

- View accepted contracts

- AI Capabilities

- Requirement extraction from tender text

- Semantic SKU matching

- Automated pricing computation

- AI-generated proposal summaries

- Best-applicant recommendation using LLM

--- 
🏗️ Tech Stack
Layer	Technology
Backend	FastAPI + SQLModel
Frontend	HTML, CSS, Vanilla JS
Database	SQLite
AI Engine	Ollama (phi3:mini)
Containers	Docker + Docker Compose
Reverse Proxy	Nginx
📦 Project Structure
```
AI_Agent/
├── backend/
│   ├── app/
│   │   ├── routes_*.py
│   │   ├── pipeline.py
│   │   ├── models.py
│   │   ├── auth_helpers.py
│   │   └── main.py
│   └── Dockerfile
│
├── frontend/
│   ├── admin/
│   ├── applicant/
│   ├── css/
│   ├── js/
│   └── Dockerfile
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

### ⚙️ Prerequisites

Make sure you have:

Docker ≥ 24

Docker Compose

Ollama installed locally
👉 https://ollama.com

Check installation:
```
docker --version
docker compose version
ollama --version
```
### 🚀 Getting Started
Before step 1, ensure you git clone the repository and navigate into it:
``` 
git clone https://github.com/SmartGridX/OPTIBIDS-.git
```

🐳 Step 1: Start Docker Services

From the project root directory:
```
docker compose up --build
```

This will start:

Backend (FastAPI)

Frontend (Nginx)

AI agent integration (Ollama via API)
To stop services, press `CTRL + C` and run:
```
docker compose down --volumes
```

🌐 Step 2: Access the Application
Service	URL
Frontend	http://localhost:3000

Backend API	http://localhost:8000

Ollama API	http://localhost:11434

🔧 Step 3: Initial Setup
pull phi3:mini model for local AI inference:

```
docker exec -it ollama ollama pull phi3:mini        
```
note:  make sure that you run this command only after the ollama container is up and running.
👤 Step 4: Create Accounts
Register Admin

Role: admin

Used to create tenders & send offers

Register Applicant

Role: applicant

Used to submit proposals

🧪 Step 5: Test Workflow
Admin Flow

Login as Admin

Create a Tender

View Applications

Generate AI Summary

Send Offer

Applicant Flow

Login as Applicant

Browse Public Tenders

Submit Proposal

Receive Offer

Accept / Reject Offer

View Accepted Offers

🤖 AI Evaluation Pipeline (Internal)

Requirement Extraction (LLM)

SKU Embedding & Matching

Pricing Calculation

Proposal Consolidation

Best Applicant Selection

🔐 Authentication

JWT-based authentication

Role-based access control

Secure token handling

📄 Environment Variables (Optional)

Create .env if needed:

SECRET_KEY=your_secret_key_here

🧹 Clean Shutdown
docker compose down


To remove volumes:

docker compose down -v

🧠 Model Notes

phi3:mini was chosen for:

Low memory footprint

Fast inference

Offline capability

You can swap models easily via Ollama

🚀 Future Enhancements

Multi-currency pricing

Vendor scoring dashboard

PDF proposal export

Cloud deployment

RAG-based tender understanding

---

🏁 Conclusion

OPTIBIDS demonstrates how AI can modernize enterprise procurement by:

Reducing manual evaluation

Improving fairness and transparency

Accelerating decision-making