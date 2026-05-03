async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderMarkdown(text) {
  const lines = text.split("\n");
  let html = "";
  let inUl = false, inOl = false, inP = false;

  function closeLists() {
    if (inUl) { html += "</ul>"; inUl = false; }
    if (inOl) { html += "</ol>"; inOl = false; }
  }
  function closeP() {
    if (inP) { html += "</p>"; inP = false; }
  }

  for (let line of lines) {
    if (/^## (.+)/.test(line)) {
      closeLists(); closeP();
      html += `<h3 class="insight-heading">${line.replace(/^## /, "")}</h3>`;
    } else if (/^# (.+)/.test(line)) {
      closeLists(); closeP();
      html += `<h3 class="insight-heading">${line.replace(/^# /, "")}</h3>`;
    } else if (/^\d+\. (.+)/.test(line)) {
      closeP();
      if (inUl) { html += "</ul>"; inUl = false; }
      if (!inOl) { html += "<ol>"; inOl = true; }
      html += `<li>${line.replace(/^\d+\. /, "").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</li>`;
    } else if (/^[-•] (.+)/.test(line)) {
      closeP();
      if (inOl) { html += "</ol>"; inOl = false; }
      if (!inUl) { html += "<ul>"; inUl = true; }
      html += `<li>${line.replace(/^[-•] /, "").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</li>`;
    } else if (line.trim() === "") {
      closeLists(); closeP();
    } else {
      closeLists();
      if (!inP) { html += "<p>"; inP = true; }
      else html += " ";
      html += line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }
  }
  closeLists(); closeP();
  return html;
}

function getDomain(url) {
  try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return ""; }
}

function getTopicClass(tags) {
  const t = (tags[0] || "").toLowerCase();
  if (/humanoid|robot|locomotion|manipulation|dexterous|legged|tactile|sim-to-real/.test(t)) return "topic-embodied";
  if (/agent|planning|reasoning|tool use|multi-agent/.test(t)) return "topic-agentic";
  if (/physics|simulation|differentiable|neural physics/.test(t)) return "topic-physics";
  if (/quantum/.test(t)) return "topic-quantum";
  return "topic-default";
}

const TOPIC_ICONS = {
  "topic-embodied": "🤖",
  "topic-agentic":  "🧠",
  "topic-physics":  "⚛️",
  "topic-quantum":  "💫",
  "topic-default":  "🔬",
};

// ── TAB DEFINITIONS ──────────────────────────────────────────────────────────

const TABS = {
  all: {
    label: "General AI Trends",
    keywords: [],   // empty = show all
    trendsTitle: "Weekly Trends — All AI",
  },
  embodied: {
    label: "Embodied AI",
    keywords: ["humanoid", "locomotion", "manipulation", "dexterous", "whole-body",
               "sim-to-real", "world model", "vision-language-action", "legged",
               "autonomous navigation", "tactile", "hardware", "imitation learning"],
    trendsTitle: "Weekly Trends — Embodied AI",
  },
  agentic: {
    label: "Agentic AI",
    keywords: ["agentic", "multi-agent", "tool use", "ai planning", "ai reasoning",
               "autonomous agent", "agent framework"],
    trendsTitle: "Weekly Trends — Agentic AI",
  },
  physics: {
    label: "Physics-based AI",
    keywords: ["physics simulation", "physics-informed", "differentiable simulation",
               "neural physics", "generative physics"],
    trendsTitle: "Weekly Trends — Physics-based AI",
  },
  quantum: {
    label: "Quantum AI",
    keywords: ["quantum machine learning", "quantum computing", "quantum algorithm",
               "quantum hardware", "quantum neural"],
    trendsTitle: "Weekly Trends — Quantum AI",
  },
};

let activeTab = "all";

// ── PHOTO HELPERS ─────────────────────────────────────────────────────────────

const TOPIC_KEYWORDS = {
  "humanoid":               "humanoid,robot",
  "locomotion":             "robot,walking",
  "manipulation":           "robot,arm",
  "dexterous hands":        "robot,hand",
  "whole-body control":     "humanoid,robot",
  "sim-to-real":            "simulation,technology",
  "world models":           "artificial,intelligence",
  "vision-language-action": "computer,vision",
  "reinforcement learning": "machine,learning",
  "imitation learning":     "robot,learning",
  "legged robots":          "robot,legs",
  "autonomous navigation":  "autonomous,robot",
  "tactile sensing":        "robot,sensor",
  "hardware":               "robotics,hardware",
  "agentic ai":             "artificial,intelligence",
  "multi-agent systems":    "technology,network",
  "tool use":               "computer,technology",
  "ai planning":            "artificial,intelligence",
  "ai reasoning":           "artificial,intelligence",
  "physics simulation":     "physics,simulation",
  "physics-informed ml":    "science,technology",
  "quantum machine learning":"quantum,technology",
  "quantum computing":      "quantum,computer",
  "foundation models":      "artificial,intelligence",
  "large language models":  "language,technology",
  "investment/funding":     "technology,startup",
  "policy/regulation":      "technology,policy",
};

function titleSeed(title) {
  var h = 0;
  for (var i = 0; i < title.length; i++) h = ((h << 5) - h + title.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function getPhotoUrl(tags, title) {
  var keywords = "artificial,intelligence";
  if (tags.length > 0) {
    var key = tags[0].toLowerCase();
    for (var k in TOPIC_KEYWORDS) {
      if (key.indexOf(k) !== -1 || k.indexOf(key) !== -1) {
        keywords = TOPIC_KEYWORDS[k];
        break;
      }
    }
  }
  var seed = titleSeed(title) % 9000 + 1000;
  return "https://loremflickr.com/600/340/" + keywords + "?lock=" + seed;
}

// ── RENDER HELPERS ────────────────────────────────────────────────────────────

function significanceBadge(sig) {
  const cls = sig === "high" ? "badge-high" : sig === "medium" ? "badge-medium" : "badge-low";
  return `<span class="badge ${cls}">${sig || "?"}</span>`;
}

function renderArticle(a) {
  const tags = (a.tags || "").split(",").map(t => t.trim()).filter(Boolean);
  const tagBadges = tags.map(t => `<span class="badge badge-topic">${t}</span>`).join(" ");
  const company = a.company ? `<span class="badge badge-company">${a.company}</span>` : "";
  const date = a.published ? new Date(a.published).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "";
  const sigClass = a.significance ? `sig-${a.significance}` : "";
  const topicClass = getTopicClass(tags);
  const topicIcon = TOPIC_ICONS[topicClass];
  const graphicLabel = tags[0] || a.source || "ai";
  const domain = getDomain(a.url);
  const favicon = domain ? `<img class="source-favicon" src="https://www.google.com/s2/favicons?domain=${domain}&sz=16" alt="" onerror="this.style.display='none'"/>` : "";

  return `
    <div class="article-card ${sigClass}">
      <a href="${a.url}" target="_blank" rel="noopener" style="text-decoration:none;">
        <div class="article-graphic ${topicClass}">
          <span class="article-graphic-icon">${topicIcon}</span>
          <img class="article-graphic-img" src="${getPhotoUrl(tags, a.title)}" alt="${graphicLabel}" loading="lazy" onerror="this.style.display='none'"/>
          <span class="graphic-topic-label">${graphicLabel}</span>
        </div>
      </a>
      <div class="article-card-body">
        <div class="article-source-row">
          ${favicon}
          <span class="article-source">${a.source}</span>
          ${date ? `<span class="article-date">${date}</span>` : ""}
        </div>
        <div class="article-title"><a href="${a.url}" target="_blank" rel="noopener">${a.title}</a></div>
        <div class="article-meta">
          ${company}
          ${significanceBadge(a.significance)}
          ${tagBadges}
        </div>
        <div class="article-summary">${a.summary || ""}</div>
      </div>
    </div>`;
}

// ── DATA LOADING ──────────────────────────────────────────────────────────────

async function loadFilters() {
  try {
    const { sources, companies } = await fetchJSON("/api/filters");
    const srcSel = document.getElementById("filter-source");
    srcSel.innerHTML = '<option value="">All Sources</option>';
    sources.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s; opt.textContent = s;
      srcSel.appendChild(opt);
    });
    const coSel = document.getElementById("filter-company");
    coSel.innerHTML = '<option value="">All Companies</option>';
    companies.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c; opt.textContent = c;
      coSel.appendChild(opt);
    });
  } catch (e) { console.error("Failed to load filters", e); }
}

async function loadTrends(tab) {
  const box = document.getElementById("trends-content");
  box.innerHTML = "Loading...";
  try {
    const data = await fetchJSON("/api/trends?topic=" + (tab || "all"));
    box.innerHTML = renderMarkdown(data.report || "No trends yet.");
    if (data.generated_at) {
      document.getElementById("trends-date").textContent =
        "Generated: " + new Date(data.generated_at).toLocaleString();
    } else {
      document.getElementById("trends-date").textContent = "";
    }
  } catch (e) {
    box.textContent = "Failed to load trends.";
  }
}

async function loadSignals(tab) {
  const box = document.getElementById("signals-content");
  box.innerHTML = "Loading...";
  try {
    const data = await fetchJSON("/api/signals?topic=" + (tab || "all"));
    box.innerHTML = renderMarkdown(data.report || "No signals yet.");
    if (data.generated_at) {
      document.getElementById("signals-date").textContent =
        "Generated: " + new Date(data.generated_at).toLocaleString();
    } else {
      document.getElementById("signals-date").textContent = "";
    }
  } catch (e) {
    box.textContent = "Failed to load signals.";
  }
}

let allArticles = [];

function articleMatchesTab(a, tab) {
  if (tab === "all") return true;
  const tabKeywords = TABS[tab].keywords;
  const tagsLower = (a.tags || "").toLowerCase();
  const titleLower = (a.title || "").toLowerCase();
  return tabKeywords.some(kw => tagsLower.includes(kw) || titleLower.includes(kw));
}

function renderArticleList() {
  const source     = document.getElementById("filter-source").value;
  const company    = document.getElementById("filter-company").value;
  const significance = document.getElementById("filter-significance").value;
  const list = document.getElementById("articles-list");

  var filtered = allArticles.filter(a => articleMatchesTab(a, activeTab));
  if (source)      filtered = filtered.filter(a => a.source === source);
  if (company)     filtered = filtered.filter(a => (a.company || "").toLowerCase().includes(company.toLowerCase()));
  if (significance)filtered = filtered.filter(a => a.significance === significance);

  document.getElementById("article-count").textContent = "(" + filtered.length + ")";
  if (filtered.length === 0) {
    list.innerHTML = "<div class='empty-state'><div class='empty-state-icon'>🔭</div>No articles found. Run a scan to populate.</div>";
  } else {
    list.innerHTML = filtered.map(renderArticle).join("");
  }
}

function updateStats() {
  const total = allArticles.length;
  const sources = new Set(allArticles.map(a => a.source).filter(Boolean)).size;
  const dates = allArticles.map(a => a.published).filter(Boolean).sort().reverse();
  const latest = dates[0]
    ? new Date(dates[0]).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })
    : "—";
  document.getElementById("stat-articles").textContent = total || "—";
  document.getElementById("stat-sources").textContent = sources || "—";
  document.getElementById("stat-latest").textContent = latest;
}

function updateLastUpdated() {
  const el = document.getElementById("last-updated");
  el.textContent = "Updated " + new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

async function loadArticles() {
  const list = document.getElementById("articles-list");
  list.innerHTML = "<div class='empty-state'><div class='empty-state-icon'>⏳</div>Loading...</div>";
  try {
    allArticles = await fetchJSON("/api/articles?limit=200");
    renderArticleList();
    updateStats();
    updateLastUpdated();
  } catch (e) {
    list.innerHTML = "<div class='empty-state'><div class='empty-state-icon'>⚠️</div>Failed to load articles.</div>";
  }
}

// ── TAB SWITCHING ─────────────────────────────────────────────────────────────

function switchTab(tab) {
  activeTab = tab;

  // Update tab button styles
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });

  // Fade out, update content, fade in
  const content = document.getElementById("tab-content");
  content.classList.add("fading");
  setTimeout(() => {
    document.getElementById("trends-title").textContent = TABS[tab].trendsTitle;
    document.getElementById("articles-title").textContent =
      tab === "all" ? "Latest Articles" : TABS[tab].label + " — Latest Articles";
    loadTrends(tab);
    loadSignals(tab);
    renderArticleList();
    content.classList.remove("fading");
  }, 200);
}

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => switchTab(btn.dataset.tab));
});

document.getElementById("apply-filters").addEventListener("click", renderArticleList);

// ── SCAN PROGRESS ─────────────────────────────────────────────────────────────

let scanPollInterval = null;

function updateProgressBar(processed, total, saved) {
  const wrap = document.getElementById("scan-progress-wrap");
  const bar = document.getElementById("scan-progress-bar");
  const label = document.getElementById("scan-progress-label");
  wrap.style.setProperty("display", "block", "important");
  const pct = total > 0 ? Math.round((processed / total) * 100) : 0;
  bar.style.width = pct + "%";
  label.textContent = `${processed} / ${total} items processed — ${saved} saved`;
}

function hideProgressBar() {
  document.getElementById("scan-progress-wrap").style.display = "none";
  document.getElementById("scan-progress-bar").style.width = "0%";
}

function startScanPolling() {
  const btn = document.getElementById("scan-btn");
  const status = document.getElementById("scan-status");

  if (scanPollInterval) clearInterval(scanPollInterval);

  scanPollInterval = setInterval(async () => {
    try {
      const state = await fetchJSON("/api/scan/status");
      if (state.total > 0) updateProgressBar(state.processed, state.total, state.saved);
      if (!state.running) {
        clearInterval(scanPollInterval);
        scanPollInterval = null;
        btn.disabled = false;
        btn.textContent = "Run Scan";
        btn.classList.remove("scanning");
        status.textContent = "Scan complete. Refreshing results...";
        await Promise.all([loadArticles(), loadTrends(activeTab), loadSignals(activeTab), loadFilters()]);
        status.textContent = `Scan complete — ${state.saved} articles saved.`;
        setTimeout(hideProgressBar, 3000);
      }
    } catch (e) { /* ignore polling errors */ }
  }, 4000);
}

document.getElementById("scan-btn").addEventListener("click", async () => {
  const btn = document.getElementById("scan-btn");
  const status = document.getElementById("scan-status");
  btn.disabled = true;
  btn.textContent = "Scanning...";
  btn.classList.add("scanning");
  status.textContent = "Scan started — this may take a few minutes.";
  try {
    await fetch("/api/scan", { method: "POST" });
    startScanPolling();
  } catch (e) {
    status.textContent = "Failed to start scan.";
    btn.disabled = false;
    btn.textContent = "Run Scan";
  }
});

// ── INIT ──────────────────────────────────────────────────────────────────────

loadFilters();
loadTrends("all");
loadSignals("all");
loadArticles();

(async () => {
  try {
    const state = await fetchJSON("/api/scan/status");
    if (state.running) {
      const btn = document.getElementById("scan-btn");
      const status = document.getElementById("scan-status");
      btn.disabled = true;
      btn.textContent = "Scanning...";
      btn.classList.add("scanning");
      status.textContent = "Scan in progress...";
      startScanPolling();
    }
  } catch (e) { /* ignore */ }
})();
