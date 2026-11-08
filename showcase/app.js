// The shell: a list of items, controls, and one iframe. All view state lives in the hash.
const $ = (id) => document.getElementById(id);
const [{ items }, { themes }] = await Promise.all([fetch("manifest.json").then((r) => r.json()), fetch("themes.json").then((r) => r.json())]);

const CONTROLS = [
  { key: "theme", label: "Theme", options: themes.map((t) => [t.id, t.label]) },
  { key: "mode", label: "Mode", options: [["light", "Light"], ["dark", "Dark"]] },
  { key: "width", label: "Width", options: [390, 768, 1024, 1440, 1920].map((w) => [String(w), String(w)]) },
  { key: "density", label: "Density", options: [["comfortable", "Comfortable"], ["compact", "Compact"]] },
  { key: "reduced", label: "Motion", options: [["0", "On"], ["1", "Reduced"]] },
  { key: "content", label: "Content", options: [["normal", "Normal"], ["long", "Long"]] },
];
const SELECTS = [
  { key: "type", label: "Type", options: ["even", "quiet", "loud"] },
  { key: "bands", label: "Bands", options: ["plain", "banded", "ruled"] },
  { key: "heads", label: "Heads", options: ["left", "side", "center"] },
  { key: "images", label: "Images", options: ["natural", "framed", "mono"] },
];
const DEFAULTS = { item: items[0].id, theme: themes[0].id, mode: "", width: "1440", density: "comfortable", reduced: "0", content: "normal", type: "even", bands: "plain", heads: "left", images: "natural" };

function read() {
  const state = { ...DEFAULTS, ...Object.fromEntries(new URLSearchParams(location.hash.slice(1))) };
  if (!items.some((i) => i.id === state.item)) state.item = items[0].id;
  if (!state.mode) state.mode = themes.find((t) => t.id === state.theme)?.mode || "light";
  return state;
}
function write(change) {
  const next = { ...read(), ...change };
  if (change.theme && !change.mode) next.mode = themes.find((t) => t.id === change.theme).mode;
  location.hash = new URLSearchParams(Object.entries(next).filter(([k, v]) => DEFAULTS[k] !== v)).toString();
}

function renderUrl(state) {
  const params = new URLSearchParams({ item: state.item, theme: state.theme, mode: state.mode });
  if (state.density !== "comfortable") params.set("density", state.density);
  if (state.reduced === "1") params.set("reduced", "1");
  if (state.content === "long") params.set("content", "long");
  for (const { key } of SELECTS) if (state[key] !== DEFAULTS[key]) params.set(key, state[key]);
  return "render.html?" + params;
}

// Controls
for (const control of CONTROLS) {
  const group = document.createElement("div");
  group.className = "group";
  group.innerHTML = `<span>${control.label}</span>`;
  for (const [value, label] of control.options) {
    const button = document.createElement("button");
    button.textContent = label;
    button.dataset.key = control.key;
    button.dataset.value = value;
    button.addEventListener("click", () => write({ [control.key]: value }));
    group.append(button);
  }
  $("bar").append(group);
}
for (const control of SELECTS) {
  const group = document.createElement("label");
  group.className = "group";
  group.innerHTML = `<span>${control.label}</span>`;
  const select = document.createElement("select");
  select.dataset.select = control.key;
  select.innerHTML = control.options.map((o) => `<option>${o}</option>`).join("");
  select.addEventListener("change", () => write({ [control.key]: select.value }));
  group.append(select);
  $("bar").append(group);
}

// List
function drawList(filter) {
  const list = $("list");
  list.textContent = "";
  let group = null;
  for (const item of items) {
    if (filter && !(item.title + " " + item.group + " " + item.id).toLowerCase().includes(filter)) continue;
    if (item.group !== group) {
      group = item.group;
      const heading = document.createElement("h2");
      heading.textContent = group;
      list.append(heading);
    }
    const link = document.createElement("a");
    link.textContent = item.title;
    link.dataset.id = item.id;
    link.href = "#";
    link.addEventListener("click", (event) => { event.preventDefault(); write({ item: item.id }); });
    list.append(link);
  }
  markList();
}
function markList() {
  const { item } = read();
  document.querySelectorAll("#list a").forEach((a) => {
    if (a.dataset.id === item) { a.setAttribute("aria-current", "page"); a.scrollIntoView({ block: "nearest" }); }
    else a.removeAttribute("aria-current");
  });
}
$("search").addEventListener("input", (event) => drawList(event.target.value.trim().toLowerCase()));

// Stage: the iframe keeps its real width, so media queries respond, and is scaled to fit.
function fit() {
  const { width } = read();
  const w = Number(width);
  const stage = $("stage");
  const room = stage.clientWidth - 24;
  const scale = Math.min(1, room / w);
  const height = (stage.clientHeight - 24) / scale;
  const frame = $("frame");
  frame.style.width = w + "px";
  frame.style.height = height + "px";
  frame.style.transform = `scale(${scale})`;
  $("scaler").style.width = w * scale + "px";
  $("meta").textContent = `${w}px${scale < 1 ? ` shown at ${Math.round(scale * 100)}%` : ""}`;
}
new ResizeObserver(fit).observe($("stage"));

// Source
let sources = [];
let activeSource = 0;
function showSource(index) {
  activeSource = index;
  document.querySelectorAll("#tabs button").forEach((b, i) => b.setAttribute("aria-pressed", String(i === index)));
  $("code").textContent = sources[index]?.text || "";
}
async function loadSources(item) {
  const fileUrl = new URL("/" + item.file, location.origin);
  const html = await (await fetch(fileUrl)).text();
  const match = html.match(/<!-- sample:start -->\n?([\s\S]*?)<!-- sample:end -->/);
  sources = [{ name: "HTML", text: match ? match[1].trim() : html }];
  const doc = new DOMParser().parseFromString(html, "text/html");
  for (const link of doc.querySelectorAll('link[rel="stylesheet"]')) {
    const url = new URL(link.getAttribute("href"), fileUrl);
    if (/\/(components|sections|effects)\//.test(url.pathname)) sources.push({ name: url.pathname.split("/").slice(-2).join("/"), text: await (await fetch(url)).text() });
  }
  const inline = [...doc.querySelectorAll("style")].map((s) => s.textContent.trim()).join("\n\n");
  if (inline) sources.push({ name: "Inline CSS", text: inline });
  if (/data-(reveal|count|timeline|nav|parallax|form)\b/.test(html)) sources.push({ name: "motion/motion.js", text: await (await fetch("/skills/ui-craft/assets/kit/motion/motion.js")).text() });
  const tabs = $("tabs");
  tabs.textContent = "";
  sources.forEach((source, i) => {
    const button = document.createElement("button");
    button.textContent = source.name;
    button.addEventListener("click", () => showSource(i));
    tabs.append(button);
  });
  showSource(0);
}
$("source-toggle").addEventListener("click", () => {
  const open = $("source").hidden;
  $("source").hidden = !open;
  $("source-toggle").setAttribute("aria-expanded", String(open));
  fit();
});
$("copy").addEventListener("click", async () => {
  await navigator.clipboard.writeText(sources[activeSource]?.text || "");
  $("copy").textContent = "Copied";
  setTimeout(() => { $("copy").textContent = "Copy"; }, 1200);
});

// Navigation
function step(by) {
  const index = items.findIndex((i) => i.id === read().item);
  write({ item: items[(index + by + items.length) % items.length].id });
}
$("prev").addEventListener("click", () => step(-1));
$("next").addEventListener("click", () => step(1));
$("replay").addEventListener("click", () => $("frame").contentWindow.location.reload());
document.addEventListener("keydown", (event) => {
  if (event.target.matches("input, select, textarea")) return;
  if (event.key === "ArrowLeft") step(-1);
  if (event.key === "ArrowRight") step(1);
});

let shownItem = null;
let shownUrl = null;
async function update() {
  const state = read();
  const item = items.find((i) => i.id === state.item);
  document.querySelectorAll("[data-key]").forEach((b) => b.setAttribute("aria-pressed", String(state[b.dataset.key] === b.dataset.value)));
  document.querySelectorAll("[data-select]").forEach((s) => { s.value = state[s.dataset.select]; });
  $("name").textContent = `${item.group}: ${item.title}`;
  document.title = `${item.title} · ui-craft showcase`;
  const url = renderUrl(state);
  if (url !== shownUrl) { shownUrl = url; $("frame").src = url; $("alone").href = url; }
  fit();
  markList();
  if (item.id !== shownItem) { shownItem = item.id; await loadSources(item); }
}
window.addEventListener("hashchange", update);
drawList("");
update();
