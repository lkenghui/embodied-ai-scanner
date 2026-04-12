async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderMarkdown(text) {
  // Basic markdown: bullet points and bold
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
}

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
  "investment/funding":     "technology,startup",
  "policy/regulation":      "technology,policy",
};

function titleSeed(title) {
  var h = 0;
  for (var i = 0; i < title.length; i++) h = ((h << 5) - h + title.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function getPhotoUrl(tags, title) {
  var keywords = "robot,artificial,intelligence";
  if (tags.length > 0) {
    var key = tags[0].toLowerCase();
    for (var k in TOPIC_KEYWORDS) {
      if (key.indexOf(k) !== -1 || k.indexOf(key) !== -1) {
        keywords = TOPIC_KEYWORDS[k];
        break;
      }
    }
  }
  // Use a seed so same article always gets same image
  var seed = titleSeed(title) % 9000 + 1000;
  return "https://loremflickr.com/600/340/" + keywords + "?lock=" + seed;
}

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

  const photoUrl = getPhotoUrl(tags, a.title);
  const graphicLabel = tags[0] || a.source || "embodied ai";

  return `
    <div class="article-card ${sigClass}">
      <a href="${a.url}" target="_blank" rel="noopener" style="text-decoration:none;">
        <div class="article-graphic">
          <img class="article-graphic-img" src="${photoUrl}" alt="${graphicLabel}" loading="lazy" onerror="this.style.display='none'"/>
          <span class="graphic-topic-label">${graphicLabel}</span>
        </div>
      </a>
      <div class="article-card-body">
        <div class="article-source-row">
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

async function loadFilters() {
  try {
    const { sources, companies } = await fetchJSON("/api/filters");
    const srcSel = document.getElementById("filter-source");
    sources.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s; opt.textContent = s;
      srcSel.appendChild(opt);
    });
    const coSel = document.getElementById("filter-company");
    companies.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c; opt.textContent = c;
      coSel.appendChild(opt);
    });
  } catch (e) { console.error("Failed to load filters", e); }
}

async function loadTrends() {
  try {
    const data = await fetchJSON("/api/trends");
    const box = document.getElementById("trends-content");
    box.innerHTML = renderMarkdown(data.report || "No trends yet.");
    if (data.generated_at) {
      document.getElementById("trends-date").textContent =
        "Generated: " + new Date(data.generated_at).toLocaleString();
    }
  } catch (e) {
    document.getElementById("trends-content").textContent = "Failed to load trends.";
  }
}

async function loadSignals() {
  try {
    const data = await fetchJSON("/api/signals");
    const box = document.getElementById("signals-content");
    box.innerHTML = renderMarkdown(data.report || "No signals yet.");
    if (data.generated_at) {
      document.getElementById("signals-date").textContent =
        "Generated: " + new Date(data.generated_at).toLocaleString();
    }
  } catch (e) {
    document.getElementById("signals-content").textContent = "Failed to load signals.";
  }
}

let allArticles = [];

function renderArticleList() {
  var topic      = document.getElementById("filter-topic").value;
  var source     = document.getElementById("filter-source").value;
  var company    = document.getElementById("filter-company").value;
  var significance = document.getElementById("filter-significance").value;
  var list = document.getElementById("articles-list");

  var filtered = allArticles;

  if (topic)       filtered = filtered.filter(function(a) { return (a.tags || "").toLowerCase().indexOf(topic) !== -1; });
  if (source)      filtered = filtered.filter(function(a) { return a.source === source; });
  if (company)     filtered = filtered.filter(function(a) { return (a.company || "").toLowerCase().indexOf(company.toLowerCase()) !== -1; });
  if (significance)filtered = filtered.filter(function(a) { return a.significance === significance; });

  document.getElementById("article-count").textContent = "(" + filtered.length + ")";
  if (filtered.length === 0) {
    list.innerHTML = "<div class='empty-state'><div class='empty-state-icon'>🔭</div>No articles found. Run a scan to populate.</div>";
  } else {
    list.innerHTML = filtered.map(renderArticle).join("");
  }
}

async function loadArticles() {
  const list = document.getElementById("articles-list");
  list.innerHTML = "<div class='empty-state'><div class='empty-state-icon'>⏳</div>Loading...</div>";
  try {
    allArticles = await fetchJSON("/api/articles?limit=200");
    renderArticleList();
  } catch (e) {
    list.innerHTML = "<div class='empty-state'><div class='empty-state-icon'>⚠️</div>Failed to load articles.</div>";
  }
}

document.getElementById("apply-filters").addEventListener("click", renderArticleList);

let scanPollInterval = null;

function updateProgressBar(processed, total, saved) {
  const wrap = document.getElementById("scan-progress-wrap");
  const bar = document.getElementById("scan-progress-bar");
  const label = document.getElementById("scan-progress-label");
  wrap.style.display = "block";
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
      if (state.total > 0) {
        updateProgressBar(state.processed, state.total, state.saved);
      }
      if (!state.running) {
        clearInterval(scanPollInterval);
        scanPollInterval = null;
        btn.disabled = false;
        btn.textContent = "Run Scan";
        status.textContent = "Scan complete. Refreshing results...";
        await Promise.all([loadArticles(), loadTrends(), loadSignals(), loadFilters()]);
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
  status.textContent = "Scan started — this may take a few minutes.";
  try {
    await fetch("/api/scan", { method: "POST" });
    startScanPolling();
  } catch (e) {
    status.textContent = "Failed to start scan.";
    btn.disabled = false;
    btn.textContent = "Run Scan Now";
  }
});

// Init
loadFilters();
loadTrends();
loadSignals();
loadArticles();

// Auto-detect if a scan is already running on page load
(async () => {
  try {
    const state = await fetchJSON("/api/scan/status");
    if (state.running) {
      const btn = document.getElementById("scan-btn");
      const status = document.getElementById("scan-status");
      btn.disabled = true;
      btn.textContent = "Scanning...";
      status.textContent = "Scan in progress...";
      startScanPolling();
    }
  } catch (e) { /* ignore */ }
})();
