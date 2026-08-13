const state = { cases: [], metrics: null, selectedId: null, filter: "all" };

const elements = {
  table: document.querySelector("#caseTable"),
  automationRate: document.querySelector("#automationRate"),
  averageConfidence: document.querySelector("#averageConfidence"),
  priorityCases: document.querySelector("#priorityCases"),
  hoursSaved: document.querySelector("#hoursSaved"),
  queueChart: document.querySelector("#queueChart"),
  emptyState: document.querySelector("#emptyState"),
  caseDetail: document.querySelector("#caseDetail"),
  dialog: document.querySelector("#caseDialog"),
};

const formatPercent = value => `${Math.round(value * 100)}%`;
const titleCase = value => value.replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

async function loadData() {
  [state.cases, state.metrics] = await Promise.all([request("/api/cases"), request("/api/metrics")]);
  render();
}

function visibleCases() {
  if (state.filter === "priority") return state.cases.filter(item => ["critical", "high"].includes(item.priority));
  if (state.filter === "review") return state.cases.filter(item => item.flags.includes("low-confidence") || item.status === "escalated");
  return state.cases;
}

function renderMetrics() {
  elements.automationRate.textContent = formatPercent(state.metrics.automation_rate);
  elements.averageConfidence.textContent = formatPercent(state.metrics.average_confidence);
  elements.priorityCases.textContent = state.metrics.high_priority_cases;
  elements.hoursSaved.textContent = `${state.metrics.estimated_hours_saved} hrs`;
}

function renderTable() {
  elements.table.innerHTML = visibleCases().map(item => `
    <tr data-case-id="${item.id}" class="${item.id === state.selectedId ? "selected" : ""}">
      <td><span class="case-id">${item.id}</span><span class="case-source">${item.source} · ${new Date(item.created_at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"})}</span></td>
      <td><span class="classification"><span class="category-dot ${item.category}"></span>${titleCase(item.category)}</span></td>
      <td>${item.queue}</td>
      <td class="confidence-cell">${formatPercent(item.confidence)}<div class="mini-bar"><span style="width:${item.confidence * 100}%"></span></div></td>
      <td><span class="status-pill ${item.status}">${titleCase(item.status)}</span></td>
    </tr>`).join("");

  document.querySelectorAll("[data-case-id]").forEach(row => row.addEventListener("click", () => selectCase(row.dataset.caseId)));
}

function renderChart() {
  const entries = Object.entries(state.metrics.queue_distribution).sort((a, b) => b[1] - a[1]);
  const maximum = Math.max(...entries.map(([, count]) => count), 1);
  elements.queueChart.innerHTML = entries.map(([queue, count]) => `
    <div class="bar-row"><span>${queue}</span><div class="bar-track"><span style="width:${(count / maximum) * 100}%"></span></div><strong>${count}</strong></div>
  `).join("");
}

function selectCase(caseId) {
  state.selectedId = caseId;
  const item = state.cases.find(candidate => candidate.id === caseId);
  if (!item) return;
  elements.emptyState.classList.add("hidden");
  elements.caseDetail.classList.remove("hidden");
  document.querySelector("#detailId").textContent = item.id;
  const priority = document.querySelector("#detailPriority");
  priority.textContent = item.priority;
  priority.className = `priority-pill ${item.priority}`;
  document.querySelector("#detailConfidence").textContent = formatPercent(item.confidence);
  document.querySelector("#confidenceBar").style.width = `${item.confidence * 100}%`;
  document.querySelector("#detailHandoff").textContent = item.handoff_summary;
  document.querySelector("#detailTranscript").textContent = item.transcript;
  const fields = Object.entries(item.extracted_fields);
  document.querySelector("#detailFields").innerHTML = fields.length
    ? fields.map(([key, value]) => `<div class="field"><span>${titleCase(key)}</span><strong>${value}</strong></div>`).join("")
    : '<div class="field"><span>Result</span><strong>No identifiers detected</strong></div>';
  document.querySelector("#detailTimeline").innerHTML = item.audit_trail.map(event => `
    <div class="timeline-event"><div><strong>${titleCase(event.action)} · ${event.actor}</strong><small>${event.detail}</small></div></div>
  `).join("");
  renderTable();
}

function render() { renderMetrics(); renderTable(); renderChart(); if (state.selectedId) selectCase(state.selectedId); }

document.querySelector("#filters").addEventListener("click", event => {
  if (!event.target.matches("[data-filter]")) return;
  document.querySelectorAll(".filter").forEach(button => button.classList.remove("active"));
  event.target.classList.add("active");
  state.filter = event.target.dataset.filter;
  renderTable();
});

document.querySelector("#newCaseButton").addEventListener("click", () => elements.dialog.showModal());
document.querySelector("#closeDialog").addEventListener("click", () => elements.dialog.close());
document.querySelector("#caseForm").addEventListener("submit", async event => {
  event.preventDefault();
  const created = await request("/api/cases", { method: "POST", body: JSON.stringify({ source: document.querySelector("#sourceInput").value, transcript: document.querySelector("#transcriptInput").value }) });
  elements.dialog.close();
  state.selectedId = created.id;
  await loadData();
});
document.querySelector("#reviewButton").addEventListener("click", async () => {
  if (!state.selectedId) return;
  await request(`/api/cases/${state.selectedId}/review`, { method: "POST", body: JSON.stringify({ reviewer: "Demo Analyst", status: "resolved", notes: "Classification and routing confirmed during human review." }) });
  await loadData();
});
document.querySelector("#resetButton").addEventListener("click", async () => { state.selectedId = null; await request("/api/reset", { method: "POST" }); elements.caseDetail.classList.add("hidden"); elements.emptyState.classList.remove("hidden"); await loadData(); });

loadData().catch(error => { elements.table.innerHTML = `<tr><td colspan="5">Unable to load demo: ${error.message}</td></tr>`; });

