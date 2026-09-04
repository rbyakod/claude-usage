const routes = {
  "/": { provider: null, title: "Overview", subtitle: "Local Claude, Codex, and Z.ai/GLM usage" },
  "/claude": { provider: "anthropic", title: "Claude", subtitle: "Anthropic transcript usage and API-equivalent cost" },
  "/codex": { provider: "codex", title: "Codex", subtitle: "Codex session usage with reasoning tokens separated" },
  "/zai": { provider: "zai", title: "Z.ai / GLM", subtitle: "GLM API estimates and Coding Plan quota stay separate" },
};

const route = routes[location.pathname] || routes["/"];
const fmt = new Intl.NumberFormat("en-US");
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 4 });

document.body.dataset.provider = route.provider || "all";
document.querySelector("h1").textContent = route.title;
document.querySelector("#subtitle").textContent = route.subtitle;
document.querySelectorAll("nav a").forEach((link) => {
  if (link.dataset.route === location.pathname) link.classList.add("active");
});

function metric(label, value, note) {
  return `<div class="metric"><strong>${value}</strong><span>${label}</span><p class="note">${note}</p></div>`;
}

function row(cells) {
  return `<tr>${cells.map((cell) => `<td>${cell}</td>`).join("")}</tr>`;
}

function byModelCost(costs, model) {
  return (costs.by_model || []).find((item) => item.model === model) || { usd: 0, credits: 0 };
}

async function load() {
  const query = route.provider ? `?provider=${route.provider}` : "";
  const [summaryRes, recsRes] = await Promise.all([
    fetch(`/api/summary${query}`),
    fetch(`/api/recommendations${query}`),
  ]);
  const summary = await summaryRes.json();
  const recs = await recsRes.json();
  render(summary, recs.recommendations || []);
}

function render(summary, recommendations) {
  const totals = summary.totals || {};
  const costs = summary.costs || {};
  document.querySelector("#status").textContent = `Loaded ${fmt.format(totals.usage_records || 0)} usage records`;
  document.querySelector("#provider-label").textContent = `Provider: ${summary.provider}`;

  document.querySelector("#metrics").innerHTML = [
    metric("Total Tokens", fmt.format(totals.total_tokens || 0), "Exact when transcripts expose usage"),
    metric("Input", fmt.format(totals.input_tokens || 0), "Fresh prompt/context tokens"),
    metric("Cache", fmt.format((totals.cache_creation_tokens || 0) + (totals.cache_read_tokens || 0)), "Creation plus reads"),
    metric("Output", fmt.format(totals.output_tokens || 0), "Assistant output tokens"),
    metric("Reasoning", fmt.format(totals.reasoning_tokens || 0), "Separate where provided"),
    metric(route.provider === "zai" ? "Plan Credits" : "Est. USD", route.provider === "zai" ? fmt.format(costs.zai_plan_credits || 0) : money.format(costs.usd || 0), "Estimated from local rate cards"),
  ].join("");

  document.querySelector("#models").innerHTML = (summary.models || [])
    .map((item) => {
      const cost = byModelCost(costs, item.model);
      return row([item.model, fmt.format(item.count), fmt.format(item.tokens), money.format(cost.usd || 0), fmt.format(cost.credits || 0)]);
    })
    .join("") || row(["No model data", "0", "0", "$0", "0"]);

  document.querySelector("#commands").innerHTML = (summary.commands || [])
    .map((item) => row([item.command_family || "other", fmt.format(item.count), fmt.format(item.output_lines)]))
    .join("") || row(["No command data", "0", "0"]);

  document.querySelector("#recommendations").innerHTML = recommendations.length
    ? recommendations.map((rec) => `<div class="rec"><strong>${rec.title}</strong><p>${rec.detail}</p><p class="note">${rec.severity} - ${rec.source}</p></div>`).join("")
    : `<div class="rec"><strong>No warnings</strong><p>No Xcode workflow warnings found in the current local data.</p></div>`;
}

load().catch((error) => {
  document.querySelector("#status").textContent = `Failed to load local data: ${error.message}`;
});
