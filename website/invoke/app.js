const modeEl = document.getElementById("mode");
const baseUrlEl = document.getElementById("base-url");
const actionEl = document.getElementById("action");
const workflowEl = document.getElementById("workflow");
const environmentEl = document.getElementById("environment");
const inventoryEl = document.getElementById("inventory");
const terraformDirEl = document.getElementById("terraform-dir");
const serviceEl = document.getElementById("service");
const hostEl = document.getElementById("host");
const messageEl = document.getElementById("message");
const statusEl = document.getElementById("invoke-status");
const requestSummaryEl = document.getElementById("request-summary");
const responseOutputEl = document.getElementById("response-output");
const formEl = document.getElementById("invoke-form");
const resetEl = document.getElementById("reset-demo");

const defaults = {
  direct: "http://127.0.0.1:8765",
  agentkernel: "http://127.0.0.1:8010/custom"
};

function setModeBaseUrl() {
  baseUrlEl.value = defaults[modeEl.value];
}

function normalizedBaseUrl() {
  return baseUrlEl.value.replace(/\/$/, "");
}

function getEndpoint(action) {
  const base = normalizedBaseUrl();
  if (action === "health") {
    return `${base}/health`;
  }
  return `${base}/${action}`;
}

function getWorkflowPayload() {
  return {
    workflow: workflowEl.value,
    context: {
      environment: environmentEl.value,
      inventory: inventoryEl.value,
      terraform_dir: terraformDirEl.value,
      service: serviceEl.value,
      host: hostEl.value
    }
  };
}

function getRequestSpec() {
  const action = actionEl.value;
  const endpoint = getEndpoint(action);
  if (action === "health") {
    return { action, endpoint, method: "GET", payload: null };
  }
  if (action === "chat") {
    return {
      action,
      endpoint,
      method: "POST",
      payload: { message: messageEl.value }
    };
  }
  return {
    action,
    endpoint,
    method: "POST",
    payload: getWorkflowPayload()
  };
}

function escapeHtml(input) {
  return String(input)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderRequestSummary(spec) {
  const payload = spec.payload
    ? `<pre>${escapeHtml(JSON.stringify(spec.payload, null, 2))}</pre>`
    : "<p>No request body.</p>";

  requestSummaryEl.innerHTML = `
    <strong>${escapeHtml(spec.method)} ${escapeHtml(spec.endpoint)}</strong>
    <p style="margin:10px 0 14px;">Action: ${escapeHtml(spec.action)}</p>
    ${payload}
  `;
}

function setStatus(kind, text) {
  statusEl.textContent = text;
  statusEl.className = "status-chip";
  if (kind === "success") {
    statusEl.classList.add("success");
  } else if (kind === "error") {
    statusEl.classList.add("error");
  }
}

async function sendRequest(spec) {
  const init = { method: spec.method, headers: {} };

  if (spec.payload) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(spec.payload);
  }

  const response = await fetch(spec.endpoint, init);
  const raw = await response.text();
  let parsed;

  try {
    parsed = JSON.parse(raw);
  } catch {
    parsed = { raw };
  }

  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}`);
    error.details = parsed;
    throw error;
  }

  return parsed;
}

modeEl.addEventListener("change", () => {
  setModeBaseUrl();
  renderRequestSummary(getRequestSpec());
});

actionEl.addEventListener("change", () => renderRequestSummary(getRequestSpec()));
[baseUrlEl, workflowEl, environmentEl, inventoryEl, terraformDirEl, serviceEl, hostEl, messageEl].forEach((element) => {
  element.addEventListener("input", () => renderRequestSummary(getRequestSpec()));
});

resetEl.addEventListener("click", () => {
  modeEl.value = "direct";
  setModeBaseUrl();
  actionEl.value = "health";
  workflowEl.value = "assess_health";
  environmentEl.value = "lab";
  inventoryEl.value = "ansible/inventories/lab/hosts.ini";
  terraformDirEl.value = "terraform/environments/lab";
  serviceEl.value = "";
  hostEl.value = "node-2";
  messageEl.value = "what workflows do you support?";
  setStatus(null, "Idle");
  responseOutputEl.textContent = "No request sent yet.";
  renderRequestSummary(getRequestSpec());
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const spec = getRequestSpec();
  renderRequestSummary(spec);
  setStatus(null, "Loading");
  responseOutputEl.textContent = "Sending request...";

  try {
    const payload = await sendRequest(spec);
    setStatus("success", "Success");
    responseOutputEl.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    setStatus("error", "Request Failed");
    responseOutputEl.textContent = JSON.stringify(
      {
        message: error.message,
        details: error.details || "Request blocked or response was not JSON."
      },
      null,
      2
    );
  }
});

setModeBaseUrl();
renderRequestSummary(getRequestSpec());
