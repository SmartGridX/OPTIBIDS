// admin.js — FIXED & STABLE VERSION

const admin = {

  /* =========================
     CREATE TENDER
  ========================= */
  async createTender() {
    const title = document.getElementById("t-title")?.value.trim();
    const desc  = document.getElementById("t-desc")?.value.trim();
    const file  = document.getElementById("t-file")?.files[0];

    if (!title || !desc) {
      alert("Title & description required");
      return;
    }

    const form = new FormData();
    form.append("title", title);
    form.append("description", desc);
    form.append("published", "true");
    if (file) form.append("file", file);

    try {
      await api.upload("/admin/tenders", form);
      alert("Tender published");
      window.location.href = "/admin/admin_dashboard.html";
    } catch (err) {
      alert("Create failed");
      console.error(err);
    }
  },

  /* =========================
     LOAD TENDERS
  ========================= */
  async loadTenders() {
    const box = document.getElementById("tenders-list");
    if (!box) return;

    box.innerHTML = "";

    try {
      const tenders = await api.get("/admin/tenders");

      if (!Array.isArray(tenders) || tenders.length === 0) {
        box.innerHTML = "<p class='muted'>No tenders yet.</p>";
        return;
      }

      tenders.forEach(t => {
        const div = document.createElement("div");
        div.className = "tender-item";

        const attachment = (t.files && t.files.length)
          ? `<a class="auth-btn"
               href="http://localhost:8000/download/${t.files[0]}"
               target="_blank">Download Attachment</a>`
          : `<span class="muted">No attachment</span>`;

        div.innerHTML = `
          <h3>${t.title}</h3>
          <p>${t.description}</p>

          <p class="muted">Status: ${t.status}</p>
          <p class="muted">Applications: ${t.applicant_count ?? 0}</p>

          ${attachment}

          <div style="margin-top:.5rem; display:flex; gap:.5rem;">
            <button class="auth-btn"
              onclick="admin.viewApplicants(${t.id})">
              View Applicants
            </button>

            <button class="auth-btn primary"
              onclick="admin.runSummary(${t.id})">
              Read Summary
            </button>
          </div>
        `;

        box.appendChild(div);
      });

    } catch (err) {
      box.innerHTML = "<p class='error'>Failed to load tenders</p>";
      console.error(err);
    }
  },

  /* =========================
     RECENT APPLICATIONS
  ========================= */
  async loadRecentApps() {
    const box = document.getElementById("recent-apps");
    if (!box) return;

    box.innerHTML = "";

    try {
      const apps = await api.get("/admin/applications");

      if (!Array.isArray(apps) || apps.length === 0) {
        box.innerHTML = "<p class='muted'>No applications yet.</p>";
        return;
      }

      apps.slice(0, 5).forEach(a => {
        const div = document.createElement("div");
        div.className = `tender-item status-${a.status}`;

        div.innerHTML = `
          <b>${a.user_email}</b>
          <p class="muted">Tender: ${a.tender_title}</p>
          <p>Status: <b>${a.status}</b></p>

          <div class="card-actions">
            <button class="auth-btn small" onclick="admin.reviewApplication(${a.id})">
              Review
            </button>
          </div>
        `;

        box.appendChild(div);
      });

    } catch (err) {
      box.innerHTML = "<p class='error'>Failed to load applications</p>";
      console.error(err);
    }
  },

  /* =========================
     REVIEW APPLICATION (FIXED)
  ========================= */
  reviewApplication(appId) {
    localStorage.setItem("review_app_id", appId);

    // 🔥 FIX: absolute path avoids nginx 404
    window.location.href = "/admin/review_application.html";
  },

  async loadApplicationForReview() {
  const appId = localStorage.getItem("review_app_id");
  if (!appId) {
    alert("No application selected");
    return;
  }

  try {
    const app = await api.get(`/admin/applications/${appId}`);

    document.getElementById("app-text").innerHTML = `
Applicant: ${app.user_email}
Tender: ${app.tender_title}
Status: ${app.status}

------------------------------------

${app.applicant_text}
    `;
  } catch (e) {
    document.getElementById("app-text").innerText =
      "Failed to load application.";
    console.error(e);
  }
},

  async sendOffer() {
    const appId = localStorage.getItem("review_app_id");
    const text = document.getElementById("offer-text")?.value.trim();

    if (!appId || !text) {
      alert("Offer text required");
      return;
    }

    try {
      await api.post(`/admin/applications/${appId}/offer`, {
        message: text
      });

      alert("Offer sent");
      window.location.href = "/admin/admin_dashboard.html";
    } catch (err) {
      alert("Failed to send offer");
      console.error(err);
    }
  },

  /* =========================
     AI SUMMARY
  ========================= */
async runSummary(tenderId) {
  let section = document.getElementById("summary-section");

  // Create section only once
  if (!section) {
    section = document.createElement("section");
    section.id = "summary-section";
    section.className = "section-card";
    section.style.marginTop = "2rem";
    section.style.display = "none";

    document.querySelector(".dash-container").appendChild(section);
  }

  section.style.display = "block";
  section.innerHTML = "<p class='muted'>Running AI evaluation…</p>";

  try {
    const res = await api.post(`/admin/tenders/${tenderId}/summary`, {});

    if (res.error) {
      section.innerHTML = `<p class="muted">${res.error}</p>`;
      return;
    }

    const best = res.best_application;

    section.innerHTML = `
      <h3>🏆 Best Application</h3>

      <p><b>Email:</b> ${best.email}</p>
      <p><b>Price:</b> ${best.price}</p>
      <p><b>SKU:</b> ${best.sku}</p>
      <p><b>Verdict:</b> ${best.verdict}</p>
      <p>${best.brief}</p>

      <hr />

      <h4>All Applications</h4>
      ${res.comparison.map(a => `
        <div class="tender-item">
          <p><b>${a.email}</b></p>
          <p><b>Price:</b> ${a.price}</p>
          <p><b>Strengths:</b> ${a.strengths.join(", ")}</p>
          <p><b>Weaknesses:</b> ${a.weaknesses.join(", ")}</p>
        </div>
      `).join("")}
    `;

  } catch (err) {
    section.innerHTML = "<p class='error'>Summary failed</p>";
    console.error(err);
  }
},
  viewApplicants(tenderId) {
    localStorage.setItem("view_tender_id", tenderId);
    window.location.href = "/admin/review_application.html";
  }
};


/* =========================
   AUTO LOAD (ADMIN DASHBOARD)
========================= */
if (location.pathname.includes("admin_dashboard.html")) {
  (async () => {
    await api.get("/auth/me");
    admin.loadTenders();
    admin.loadRecentApps();
  })();
}

window.admin = admin;
