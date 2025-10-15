// ------------------------------------------------------------
// PredictWell - Frontend JS
// ------------------------------------------------------------

// Helper
const $ = (s) => document.querySelector(s);

// If you ever run this on a different port/host, change here:
const API_BASE = "http://127.0.0.1:8000";

// ---------------- Health check ----------------
const btnHealth = $("#btnHealth");
if (btnHealth) {
  btnHealth.addEventListener("click", async () => {
    $("#healthOut").textContent = "Checking…";
    try {
      const r = await fetch(`${API_BASE}/api/health`);
      const j = await r.json();
      $("#healthOut").textContent = JSON.stringify(j, null, 2);
    } catch (e) {
      $("#healthOut").textContent = "Health check failed: " + e;
    }
  });
}

// ---------------- Risk form submit ----------------
const riskForm = $("#riskForm");
if (riskForm) {
  riskForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // do not refresh page

    const fd = new FormData(riskForm);

    // Core features currently supported by the backend:
    const payload = {
      age: Number(fd.get("age")),
      sex: String(fd.get("sex")),
      heart_rate: Number(fd.get("heart_rate")),
      blood_pressure_sys: Number(fd.get("blood_pressure_sys")),
      respiration_rate: Number(fd.get("respiration_rate")),
      oxygen_saturation: Number(fd.get("oxygen_saturation")),
      gait_speed: Number(fd.get("gait_speed")),
      step_variability: Number(fd.get("step_variability")),
      hrv: Number(fd.get("hrv")),
      sleep_hours: Number(fd.get("sleep_hours")),
      recent_fall: String(fd.get("recent_fall")) === "true",
      mobility_aid: String(fd.get("mobility_aid")),
    };

    // NEW fields you added in the UI.
    // NOTE: Your current FastAPI model will IGNORE these extras
    // until we update the backend schema in the next step.
    payload.cognitive_score   = Number(fd.get("cognitive_score"));
    payload.balance_test      = Number(fd.get("balance_test"));
    payload.medication_count  = Number(fd.get("medication_count"));

    $("#riskOut").textContent = "Computing…";

    try {
      const r = await fetch(`${API_BASE}/api/risk-score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const j = await r.json();
      $("#riskOut").textContent = JSON.stringify(j, null, 2);

      // ---- Show colored badge (Low / Moderate / High) ----
      const badge = $("#riskBadge");
      if (badge) {
        badge.classList.remove("low", "moderate", "high");

        const score = Number(j?.risk_score ?? 0);
        let label = "Low";
        let cls = "low";

        if (score >= 6 && score <= 15) {
          label = "Moderate";
          cls = "moderate";
        } else if (score > 15) {
          label = "High";
          cls = "high";
        }

        badge.textContent = `Risk Level: ${label} (score ${score})`;
        badge.classList.add(cls);
      }
    } catch (e) {
      $("#riskOut").textContent = "Error: " + e;
    }
  });
}

// ---------------- CSV upload (optional) ----------------
const btnUpload = $("#btnUpload");
if (btnUpload) {
  btnUpload.addEventListener("click", async () => {
    const f = $("#csvFile").files[0];
    if (!f) {
      $("#uploadOut").textContent = "Pick a CSV first.";
      return;
    }

    const fd = new FormData();
    fd.append("file", f, f.name);

    try {
      const r = await fetch(`${API_BASE}/api/upload-csv`, {
        method: "POST",
        body: fd,
      });
      const j = await r.json();
      $("#uploadOut").textContent = JSON.stringify(j, null, 2);
    } catch (e) {
      $("#uploadOut").textContent = "Upload error: " + e;
    }
  });
}
