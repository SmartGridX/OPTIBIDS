// applicant.js
const applicant = {

  /* =========================
     LOAD PUBLIC TENDERS
  ========================= */
  async loadTenders() {
    try {
      const tenders = await api.get("/tenders");
      const box = document.getElementById("public-tenders");

      box.innerHTML = "";

      if (!Array.isArray(tenders) || !tenders.length) {
        box.innerHTML = "<p class='muted'>No public tenders available.</p>";
        return;
      }

      tenders.forEach(t => {
        const div = document.createElement("div");
        div.className = "tender-item";

        div.innerHTML = `
          <h3>${t.title}</h3>
          <p>${t.description}</p>

          <button class="auth-btn primary"
            onclick="applicant.openApplyForm(${t.id})">
            Apply
          </button>
        `;

        box.appendChild(div);
      });

    } catch (e) {
      console.error("Failed to load tenders", e);
    }
  },

  /* =========================
     APPLY FORM
  ========================= */
  openApplyForm(tenderId) {
    document.getElementById("apply-tender-id").value = tenderId;
    document.getElementById("apply-section").style.display = "block";
  },

  async submitApplication() {
    const tenderId = Number(document.getElementById("apply-tender-id").value);
    const text = document.getElementById("apply-text").value.trim();

    if (!text) return alert("Application text required");

    const res = await api.post("/applicant/submit_application", {
      tender_id: tenderId,
      text
    });

    document.getElementById("apply-msg").innerText =
      "Application submitted (ID " + res.application_id + ")";
  },

  /* =========================
     NOTIFICATIONS (OFFERS)
  ========================= */
  async loadNotifications() {
    try {
      const offers = await api.get("/applicant/notifications");
      const box = document.getElementById("notifications");

      box.innerHTML = "";

      if (!offers.length) {
        box.innerHTML = "<p class='muted'>No offers yet.</p>";
        return;
      }

      offers.forEach(o => {
        const div = document.createElement("div");
        div.className = "tender-item";

        div.innerHTML = `
          <p><b>Offer for Tender #${o.tender_id}</b></p>
          <p>${o.offer?.message || "No details provided"}</p>

          <div class="card-actions">
            <button class="auth-btn small primary"
              onclick="applicant.respondOffer(${o.application_id}, 'accept')">
              Accept
            </button>

            <button class="auth-btn small"
              onclick="applicant.respondOffer(${o.application_id}, 'reject')">
              Reject
            </button>
          </div>
        `;

        box.appendChild(div);
      });

    } catch (e) {
      console.error("Notification load failed", e);
    }
  },

  async respondOffer(appId, decision) {
    await api.post(`/applicant/offer/${appId}/respond?decision=${decision}`);
    alert(`Offer ${decision}ed`);
    this.loadNotifications();
  }
};

/* =========================
   AUTO LOAD
========================= */
if (location.pathname.includes("applicant_dashboard.html")) {
  applicant.loadTenders();
  applicant.loadNotifications();
}

window.applicant = applicant;
