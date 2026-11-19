"use strict";

const state = {
  images: [],
  selected: new Set(),
  browsePath: null,
};

const el = (id) => document.getElementById(id);

async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

function setStatus(id, message) {
  el(id).textContent = message;
}

function renderTiles() {
  const container = el("tiles");
  container.innerHTML = "";
  state.images.forEach((image) => {
    const tile = document.createElement("div");
    tile.className = "tile" + (state.selected.has(image.path) ? " selected" : "");

    const img = document.createElement("img");
    img.src = image.thumbnail;
    img.alt = image.name;
    img.loading = "lazy";

    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = state.selected.has(image.path);
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        state.selected.add(image.path);
      } else {
        state.selected.delete(image.path);
      }
      renderTiles();
    });
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(image.name));

    tile.appendChild(img);
    tile.appendChild(label);
    container.appendChild(tile);
  });
  el("select-all").checked =
    state.images.length > 0 && state.selected.size === state.images.length;
}

async function loadImages(path) {
  setStatus("path-status", "Loading...");
  try {
    const data = await api("/api/images?path=" + encodeURIComponent(path));
    state.images = data.images;
    state.selected.clear();
    el("path-input").value = data.path;
    renderTiles();
    setStatus("path-status", data.images.length + " image(s)");
    el("export-output").value = el("export-output").value || "";
  } catch (error) {
    setStatus("path-status", "Error: " + error.message);
  }
}

async function browse(path) {
  const data = await api("/api/browse?path=" + encodeURIComponent(path));
  state.browsePath = data.path;
  const browser = el("browser");
  const list = el("browse-list");
  browser.classList.remove("hidden");
  list.innerHTML = "";
  data.directories.forEach((name) => {
    const button = document.createElement("button");
    const childPath = data.path.replace(/\/$/, "") + "/" + name;
    button.textContent = name;
    button.addEventListener("click", () => browse(childPath));
    list.appendChild(button);
  });
  el("browse-up").onclick = () => {
    if (data.parent) {
      browse(data.parent);
    } else {
      browser.classList.add("hidden");
    }
  };
}

function selectedFiles() {
  return state.images.filter((image) => state.selected.has(image.path)).map((image) => image.path);
}

async function runExport() {
  const files = selectedFiles();
  if (files.length === 0) {
    setStatus("export-status", "Select at least one image.");
    return;
  }
  const payload = {
    files,
    format: el("export-format").value,
    quality: Number(el("export-quality").value),
    reduce: el("export-reduce").checked,
    max_side: Number(el("export-max-side").value),
  };
  if (el("export-output").value) {
    payload.output = el("export-output").value;
  }
  setStatus("export-status", "Exporting...");
  try {
    const result = await api("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setStatus("export-status", `Exported ${result.files.length} file(s) to ${result.output_dir}`);
    refreshLog();
  } catch (error) {
    setStatus("export-status", "Error: " + error.message);
  }
}

function renderSettings(config) {
  const form = el("settings-form");
  form.innerHTML = "";
  const types = {
    bool: "checkbox",
    int: "number",
    float: "number",
    str: "text",
  };
  Object.entries(config).forEach(([category, values]) => {
    Object.entries(values).forEach(([name, value]) => {
      const label = document.createElement("label");
      label.textContent = `${category}.${name}`;
      const input = document.createElement("input");
      input.type = types[guessType(value)] || "text";
      input.dataset.category = category;
      input.dataset.name = name;
      if (input.type === "checkbox") {
        input.checked = Boolean(value);
      } else {
        input.value = value;
      }
      label.appendChild(input);
      form.appendChild(label);
    });
  });
}

function guessType(value) {
  if (typeof value === "boolean") return "bool";
  if (typeof value === "number") return Number.isInteger(value) ? "int" : "float";
  return "str";
}

async function openSettings() {
  const config = await api("/api/config");
  renderSettings(config);
  el("settings-dialog").showModal();
}

async function saveSettings() {
  const values = {};
  el("settings-form").querySelectorAll("input").forEach((input) => {
    const category = input.dataset.category;
    const name = input.dataset.name;
    let value;
    if (input.type === "checkbox") {
      value = input.checked;
    } else if (input.type === "number") {
      value = Number(input.value);
    } else {
      value = input.value;
    }
    values[category] = values[category] || {};
    values[category][name] = value;
  });
  await api("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(values),
  });
  el("settings-dialog").close();
}

async function refreshLog() {
  const data = await api("/api/logs?limit=200");
  el("log").textContent = data.logs.join("\n");
}

function bindEvents() {
  el("open-button").addEventListener("click", () => loadImages(el("path-input").value));
  el("browse-button").addEventListener("click", () => browse(el("path-input").value));
  el("export-button").addEventListener("click", runExport);
  el("select-all").addEventListener("change", (event) => {
    if (event.target.checked) {
      state.images.forEach((image) => state.selected.add(image.path));
    } else {
      state.selected.clear();
    }
    renderTiles();
  });
  el("settings-button").addEventListener("click", openSettings);
  el("save-settings").addEventListener("click", (event) => {
    event.preventDefault();
    saveSettings();
  });
  el("help-button").addEventListener("click", (event) => {
    event.stopPropagation();
    el("help-menu").classList.toggle("hidden");
  });
  el("about-button").addEventListener("click", () => {
    el("help-menu").classList.add("hidden");
    el("about-dialog").showModal();
  });
  document.addEventListener("click", () => el("help-menu").classList.add("hidden"));
  el("refresh-log").addEventListener("click", refreshLog);
}

async function init() {
  bindEvents();
  const config = await api("/api/config");
  const source = config.paths ? config.paths.source_dir : "";
  if (source) {
    el("path-input").value = source;
    el("export-output").value = config.paths.output_root || "";
    await loadImages(source);
  }
  await refreshLog();
}

init();