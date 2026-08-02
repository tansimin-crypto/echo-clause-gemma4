/**
 * EchoClause static demo — loads recorded pipeline JSON, no live inference.
 */
(function () {
  "use strict";

  const FIELD_LABELS = {
    platform_fee: "Platform Fee",
    total_repayment: "Total Repayment",
    late_fee: "Late Fee",
    repayment_term_days: "Repayment Term",
    automatic_debit: "Automatic Debit",
    principal: "Principal",
    interest_rate: "Interest Rate",
    processing_fee: "Processing Fee",
  };

  const SOURCE_LABELS = {
    advertisement: "Advertisement",
    sales_pitch: "Sales Pitch",
    sales_audio: "Sales Pitch (Audio)",
    support_chat: "Support Chat",
    contract: "Contract",
  };

  const EVIDENCE = [
    { id: "advertisement", label: "Ad", type: "image", src: "assets/demo_case/advertisement.png", caption: "Marketing advertisement — Nuru Credit" },
    { id: "support_chat", label: "Chat", type: "image", src: "assets/demo_case/support_chat.png", caption: "Support chat screenshot" },
    { id: "sales_pitch", label: "Audio", type: "audio", src: "assets/demo_case/sales_pitch.wav", caption: "Recorded sales pitch (WAV)" },
    { id: "contract", label: "Contract", type: "image", src: "assets/demo_case/contract.png", caption: "Loan agreement (synthetic demo)" },
  ];

  const SALES_TRANSCRIPT =
    "You will repay exactly $1,000. There are no processing charges. " +
    "Late payment is only a one-time $20 fee.";

  let demoData = null;
  let claimsById = {};

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $$(sel, root) {
    return Array.from((root || document).querySelectorAll(sel));
  }

  function labelField(field) {
    return FIELD_LABELS[field] || field.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }

  function labelSource(sourceId) {
    return SOURCE_LABELS[sourceId] || sourceId.replace(/_/g, " ");
  }

  function sourceDotClass(sourceId) {
    if (sourceId === "advertisement") return "ad";
    if (sourceId === "sales_pitch") return "audio";
    if (sourceId === "support_chat") return "chat";
    if (sourceId === "contract") return "contract";
    return "ad";
  }

  function parseEvidenceSummary(summary) {
    const parts = { promise: "", contract: "" };
    if (!summary) return parts;
    const match = summary.match(/^Promise:\s*(.+?)\s*\|\s*Contract:\s*(.+)$/i);
    if (match) {
      parts.promise = match[1].trim();
      parts.contract = match[2].trim();
    }
    return parts;
  }

  function findClaim(id) {
    return claimsById[id] || null;
  }

  function claimSourceLabel(claim) {
    if (!claim) return "";
    return labelSource(claim.source_id);
  }

  async function loadDemo() {
    const resp = await fetch("data/demo.json");
    if (!resp.ok) throw new Error(`Failed to load demo data (${resp.status})`);
    demoData = await resp.json();
    claimsById = {};
    (demoData.claims || []).forEach((c) => {
      claimsById[c.claim_id] = c;
    });
  }

  function renderHeader() {
    const count = demoData.conflict_count || (demoData.contradictions || []).length;
    const model = demoData.model_id || "google/gemma-4-E2B-it";
    const ts = demoData.timestamp_utc || "";

    $("#stat-conflicts").textContent = String(count);
    $("#stat-claims").textContent = String((demoData.claims || []).length);
    $("#stat-model").textContent = model.replace("google/", "");
    $("#footer-model").textContent = model;

    const sha = document.documentElement.dataset.gitSha || "local";
    $("#footer-sha").textContent = sha.slice(0, 12);

    if (ts) {
      $("#footer-ts").textContent = ts;
    }
  }

  function renderEvidenceGallery() {
    const tabs = $("#evidence-tabs");
    const viewer = $("#evidence-viewer");
    const caption = $("#evidence-caption");
    let active = EVIDENCE[0];

    function show(item) {
      active = item;
      $$(".evidence-tab", tabs).forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.id === item.id);
      });

      if (item.type === "audio") {
        viewer.className = "evidence-viewer audio-panel";
        viewer.innerHTML =
          `<h3>Sales Pitch Recording</h3>` +
          `<p>Synthetic WAV evidence — Gemma 4 multimodal input</p>` +
          `<audio controls src="${item.src}">Your browser does not support audio.</audio>` +
          `<div class="audio-transcript">${SALES_TRANSCRIPT}</div>`;
        viewer.onclick = null;
      } else {
        viewer.className = "evidence-viewer";
        viewer.innerHTML = `<img src="${item.src}" alt="${item.label}" loading="lazy"/>`;
        viewer.onclick = () => openLightbox(item.src, item.caption);
      }
      caption.textContent = item.caption;
    }

    tabs.innerHTML = EVIDENCE.map(
      (e) => `<button type="button" class="evidence-tab" data-id="${e.id}">${e.label}</button>`
    ).join("");

    tabs.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".evidence-tab");
      if (!btn) return;
      const item = EVIDENCE.find((e) => e.id === btn.dataset.id);
      if (item) show(item);
    });

    show(active);
  }

  function renderClaims() {
    const container = $("#claims-by-source");
    const groups = {};

    (demoData.claims || []).forEach((claim) => {
      const key = claim.source_id;
      if (!groups[key]) groups[key] = [];
      groups[key].push(claim);
    });

    const order = ["advertisement", "sales_pitch", "support_chat", "contract"];
    const keys = order.filter((k) => groups[k]);

    container.innerHTML = keys
      .map((sourceId) => {
        const claims = groups[sourceId];
        const cards = claims
          .map(
            (c) =>
              `<div class="claim-card">` +
              `<div class="claim-field">${labelField(c.field)}</div>` +
              `<div class="claim-value">${escapeHtml(c.raw_value)}</div>` +
              `<div class="claim-meta">Confidence ${Math.round((c.confidence || 0) * 100)}% · ${c.explicitness || "explicit"}</div>` +
              `</div>`
          )
          .join("");

        return (
          `<div class="source-group">` +
          `<div class="source-label"><span class="source-dot ${sourceDotClass(sourceId)}"></span>${labelSource(sourceId)}</div>` +
          cards +
          `</div>`
        );
      })
      .join("");
  }

  function renderConflicts() {
    const container = $("#conflict-list");
    const contradictions = demoData.contradictions || [];

    container.innerHTML = contradictions
      .map((c, idx) => {
        const field = labelField(c.canonical_field);
        const severity = (c.severity || "medium").toLowerCase();
        const parsed = parseEvidenceSummary(c.evidence_summary);

        const promiseIds = c.promise_claim_ids || [];
        const contractIds = c.contract_claim_ids || [];
        const promiseClaims = promiseIds.map(findClaim).filter(Boolean);
        const contractClaims = contractIds.map(findClaim).filter(Boolean);

        const promiseQuote = promiseClaims.map((cl) => cl.evidence_text || cl.raw_value).join(" · ") || parsed.promise;
        const contractQuote = contractClaims.map((cl) => cl.evidence_text || cl.raw_value).join(" · ") || parsed.contract;
        const promiseSrc = promiseClaims.map(claimSourceLabel).join(", ") || "Promise sources";
        const contractSrc = contractClaims.map(claimSourceLabel).join(", ") || "Contract";

        const diff = c.deterministic_difference
          ? `<div class="diff-line">Δ ${c.deterministic_difference}</div>`
          : "";

        return (
          `<article class="conflict-row" data-idx="${idx}">` +
          `<button type="button" class="conflict-summary" aria-expanded="false">` +
          `<span class="conflict-field">${escapeHtml(field)}</span>` +
          `<span class="conflict-badges">` +
          `<span class="severity-badge severity-${severity}">${severity}</span>` +
          `<span class="status-badge">Contradicted</span>` +
          `<span class="expand-icon">▼</span>` +
          `</span>` +
          `</button>` +
          `<div class="conflict-detail">` +
          `<div class="compare-grid">` +
          `<div class="compare-side promise">` +
          `<div class="compare-label">Promise</div>` +
          `<div class="compare-quote">"${escapeHtml(promiseQuote)}"</div>` +
          `<div class="compare-source">${escapeHtml(promiseSrc)}</div>` +
          `</div>` +
          `<div class="compare-side contract">` +
          `<div class="compare-label">Contract</div>` +
          `<div class="compare-quote">"${escapeHtml(contractQuote)}"</div>` +
          `<div class="compare-source">${escapeHtml(contractSrc)}</div>` +
          `</div>` +
          `</div>` +
          diff +
          `</div>` +
          `</article>`
        );
      })
      .join("");

    container.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".conflict-summary");
      if (!btn) return;
      const row = btn.closest(".conflict-row");
      const open = row.classList.toggle("expanded");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Expand platform fee by default (hidden fee callout)
    const first = container.querySelector('.conflict-row[data-idx="2"]') ||
      container.querySelector(".conflict-row");
    if (first) {
      first.classList.add("expanded");
      const btn = first.querySelector(".conflict-summary");
      if (btn) btn.setAttribute("aria-expanded", "true");
    }
  }

  function renderQuestions() {
    const list = $("#question-list");
    const questions = demoData.clarification_questions || [];

    const friendly = questions.map((q, i) => {
      const templates = [
        "Why does the contract include a $150 platform fee not mentioned in the ad?",
        "The ad says 30 days — why does the contract specify 21 days?",
        "Support said no auto-debit — why is authorization enabled in the contract?",
        "Is the 5% weekly late fee compounded on the full outstanding balance?",
        "Sales pitch promised $1,000 total — why does the contract show $1,150?",
      ];
      return friendlyOverride(q, templates[i] || q);
    });

    list.innerHTML = friendly
      .map(
        (q, i) =>
          `<li><span class="question-num">${i + 1}</span><span>${escapeHtml(q)}</span></li>`
      )
      .join("");
  }

  function friendlyOverride(raw, fallback) {
    if (raw && raw.length > 80) return fallback;
    return fallback || raw;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function openLightbox(src, alt) {
    const lb = $("#lightbox");
    const img = $("#lightbox-img");
    img.src = src;
    img.alt = alt || "";
    lb.classList.add("open");
  }

  function closeLightbox() {
    $("#lightbox").classList.remove("open");
  }

  function bindLightbox() {
    $("#lightbox").addEventListener("click", closeLightbox);
    $("#lightbox-close").addEventListener("click", (e) => {
      e.stopPropagation();
      closeLightbox();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeLightbox();
    });
  }

  async function init() {
    const main = $("#main-content");
    const loading = $("#loading");
    const error = $("#error");

    try {
      await loadDemo();
      loading.hidden = true;
      main.hidden = false;
      renderHeader();
      renderEvidenceGallery();
      renderClaims();
      renderConflicts();
      renderQuestions();
      bindLightbox();
    } catch (err) {
      loading.hidden = true;
      error.hidden = false;
      error.textContent = `Could not load demo: ${err.message}`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
