// Measures one rendered page. Runs inside the browser and returns plain JSON.
// Thresholds are documented in references/checks.md; keep the two in step.
() => {
  const root = document.documentElement;
  const cw = root.clientWidth; // excludes the scrollbar a visible browser shows
  const vh = window.innerHeight;
  const out = new Map();

  const add = (id, severity, message, sample) => {
    const key = id + "|" + severity;
    if (!out.has(key)) out.set(key, { id, severity, message, count: 0, samples: [] });
    const f = out.get(key);
    f.count += 1;
    if (sample && f.samples.length < 3 && !f.samples.includes(sample)) f.samples.push(sample);
  };
  const short = (t) => (t || "").replace(/\s+/g, " ").trim().slice(0, 80);
  const desc = (el) => {
    const cls = typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/)[0] : "";
    return el.tagName.toLowerCase() + (el.id ? "#" + el.id : cls);
  };
  const ownText = (el) => short([...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(" "));
  const shown = (el) => {
    const s = getComputedStyle(el);
    if (s.display === "none" || s.visibility === "hidden") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const opacityOf = (el) => {
    let o = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity);
    return o;
  };
  const isFixed = (el) => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (getComputedStyle(n).position === "fixed") return true;
    }
    return false;
  };
  const aboveThePage = (el) => el.getBoundingClientRect().bottom + window.scrollY <= 0; // a skip link waiting off-screen
  const concealed = (el) => aboveThePage(el) || el.closest('[aria-hidden="true"],[hidden],[inert],dialog:not([open])') !== null;

  const all = [...document.body.querySelectorAll("*")].filter((el) => !el.closest("script,style,noscript,template"));
  const textEls = all.filter((el) => !el.closest("svg") && ownText(el).length >= 2 && shown(el));
  const MEDIA = "img,video,canvas,iframe,svg,picture";
  const mediaEls = all.filter((el) => el.matches(MEDIA) && !el.parentElement.closest("svg") && shown(el));

  // Sideways scroll
  if (root.scrollWidth > cw + 1) {
    const culprit = all.find((el) => shown(el) && el.getBoundingClientRect().right > cw + 1);
    add("overflow", "fail", "The page scrolls sideways: " + root.scrollWidth + "px of content in " + cw + "px", culprit ? desc(culprit) : "");
  }

  // Equal side margins: the outer edges of everything that is not full-bleed
  const blocks = textEls.concat(mediaEls).filter((el) => {
    if (isFixed(el) || concealed(el) || opacityOf(el) < 0.05) return false;
    const r = el.getBoundingClientRect();
    return r.width >= 40 && r.width < cw - 2 && r.left >= 0 && r.right <= cw + 1;
  });
  if (blocks.length >= 5) {
    const left = Math.min(...blocks.map((el) => el.getBoundingClientRect().left));
    const right = cw - Math.max(...blocks.map((el) => el.getBoundingClientRect().right));
    if (Math.abs(left - right) > Math.max(8, cw * 0.02)) {
      add("margins", "fail", "Uneven side margins: left " + Math.round(left) + "px, right " + Math.round(right) + "px");
    }
  }

  // Empty bands of plain background
  const spans = textEls.concat(mediaEls)
    .filter((el) => !isFixed(el) && !concealed(el) && opacityOf(el) >= 0.05)
    .map((el) => {
      const r = el.getBoundingClientRect();
      return [r.top + window.scrollY, r.bottom + window.scrollY];
    })
    .sort((a, b) => a[0] - b[0]);
  const pageHeight = Math.max(root.scrollHeight, document.body.scrollHeight);
  let reach = spans.length ? spans[0][1] : 0;
  const gaps = [];
  for (const [top, bottom] of spans) {
    if (top - reach > 0) gaps.push([reach, top]);
    reach = Math.max(reach, bottom);
  }
  if (spans.length && pageHeight > vh && pageHeight - reach > 0) gaps.push([reach, pageHeight]); // a short page may end early
  for (const [a, b] of gaps) {
    const size = b - a;
    const where = "at " + Math.round(a) + "px, " + Math.round(size) + "px tall";
    if (size > vh) add("empty-band", "fail", "Empty band taller than one screen", where);
    else if (size > vh * 0.6) add("empty-band", "warn", "Empty band over 60% of a screen", where);
  }

  // Content still invisible after the page was scrolled through
  for (const el of textEls) {
    if (isFixed(el) || concealed(el) || getComputedStyle(el).pointerEvents === "none") continue;
    const r = el.getBoundingClientRect();
    if (r.right <= 0 || r.left >= cw) continue;
    if (opacityOf(el) < 0.05) add("hidden-content", "fail", "Text is still invisible after scrolling through the page", short(ownText(el)));
  }

  // Tap targets on small screens
  if (cw <= 820) {
    for (const el of document.querySelectorAll('a,button,input:not([type=hidden]),select,textarea,summary,[role=button]')) {
      if (!shown(el) || concealed(el)) continue;
      const inline = el.tagName === "A" && getComputedStyle(el).display === "inline"
        && short(el.parentElement.textContent).length > short(el.textContent).length + 3;
      if (inline) continue;
      const wrapped = el.matches('input[type=checkbox],input[type=radio]') && el.labels && el.labels[0]; // the label is the target
      const r = (wrapped || el).getBoundingClientRect();
      const small = Math.min(r.width, r.height);
      if (small < 24) add("tap-target", "fail", "Tap target under 24px", desc(el) + " " + short(el.textContent));
      else if (small < 44) add("tap-target", "warn", "Tap target under 44px", desc(el) + " " + short(el.textContent));
    }
  }

  // Images
  for (const img of document.images) {
    if (concealed(img)) continue;
    const src = (img.currentSrc || img.src || "").split("/").pop().slice(0, 60);
    if (img.complete && img.naturalWidth === 0 && (img.currentSrc || img.src)) add("broken-image", "fail", "Image did not load", src);
    if (!img.hasAttribute("alt")) add("img-alt", "fail", "Image has no alt attribute", src);
    if (!img.hasAttribute("width") || !img.hasAttribute("height")) add("img-size", "warn", "Image has no width and height attributes", src);
  }

  // Headings
  const heads = [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")].filter((el) => shown(el) && !concealed(el));
  const h1s = heads.filter((el) => el.tagName === "H1").length;
  if (h1s !== 1) add("h1", "fail", "The page has " + h1s + " visible h1 headings; it needs exactly one");
  let last = 0;
  for (const h of heads) {
    const level = Number(h.tagName[1]);
    if (last && level > last + 1) add("heading-order", "warn", "Heading level jumps from h" + last + " to h" + level, short(h.textContent));
    last = level;
  }

  // Text size and line length
  for (const el of textEls) {
    if (concealed(el) || ownText(el).length < 20) continue;
    const size = parseFloat(getComputedStyle(el).fontSize);
    if (size < 14) add("small-text", "warn", "Running text under 14px", size + "px: " + ownText(el).slice(0, 50));
    if (el.tagName === "P" && el.getBoundingClientRect().width / (size * 0.5) > 90) add("long-lines", "warn", "Lines over about 90 characters", desc(el));
  }

  // Contrast. A canvas turns any CSS colour (oklch, color-mix, ...) into RGBA.
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 1;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const rgba = (css) => {
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = "#000";
    ctx.fillStyle = css;
    ctx.fillRect(0, 0, 1, 1);
    const d = ctx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const over = (top, under) => {
    const a = top[3];
    return [0, 1, 2].map((i) => top[i] * a + under[i] * (1 - a)).concat(1);
  };
  const backdrop = (el) => {
    const stack = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.backgroundImage !== "none") return null; // a picture or gradient: not measurable here
      const c = rgba(s.backgroundColor);
      if (c[3] > 0) stack.push(c);
      if (c[3] === 1) break;
    }
    const dark = getComputedStyle(root).colorScheme.includes("dark");
    let base = dark ? [18, 18, 18, 1] : [255, 255, 255, 1];
    for (const c of stack.reverse()) base = over(c, base);
    return base;
  };
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const pairs = new Set();
  for (const el of textEls.slice(0, 600)) {
    if (concealed(el) || el.closest(":disabled,[aria-disabled=true]") || opacityOf(el) < 0.05) continue;
    const s = getComputedStyle(el);
    const bg = backdrop(el);
    if (!bg) continue;
    const fg = rgba(s.color);
    fg[3] *= opacityOf(el);
    const text = over(fg, bg);
    const [a, b] = [lum(text), lum(bg)].sort((x, y) => y - x);
    const ratio = (a + 0.05) / (b + 0.05);
    const size = parseFloat(s.fontSize);
    const large = size >= 24 || (size >= 18.66 && Number(s.fontWeight) >= 700);
    const key = text.join() + "|" + bg.join() + "|" + large;
    if (ratio < (large ? 3 : 4.5) && !pairs.has(key)) {
      pairs.add(key);
      add("contrast", "fail", "Text contrast below WCAG AA", ratio.toFixed(2) + ":1 on " + desc(el) + ": " + ownText(el).slice(0, 40));
    }
  }

  // Names for controls
  for (const el of document.querySelectorAll("input,select,textarea")) {
    if (!shown(el) || concealed(el) || /^(hidden|submit|button|reset|image)$/.test(el.type)) continue;
    if (!(el.labels && el.labels.length) && !el.getAttribute("aria-label") && !el.getAttribute("aria-labelledby") && !el.title) {
      add("field-label", "fail", "Form field has no label", desc(el));
    }
  }
  for (const el of document.querySelectorAll("a,button,[role=button]")) {
    if (!shown(el) || concealed(el)) continue;
    const named = short(el.textContent) || el.getAttribute("aria-label") || el.getAttribute("aria-labelledby") || el.title
      || (el.querySelector("img[alt]:not([alt=''])") !== null) || (el.querySelector("svg title") !== null);
    if (!named) add("button-name", "fail", "Link or button has no accessible name", desc(el));
  }

  // Unfinished content
  const placeholder = (document.body.innerText || "").match(/lorem ipsum|coming soon|\bTODO\b|placeholder text|your (?:name|text) here/i);
  if (placeholder) add("placeholder-text", "fail", "Unfinished placeholder text on the page", placeholder[0]);

  // Motion in the stylesheet
  for (const el of document.querySelectorAll("a,button,[role=button],input,select,textarea")) {
    const s = getComputedStyle(el);
    if (s.transitionProperty.split(",").some((p) => p.trim() === "all") && s.transitionDuration.split(",").some((d) => parseFloat(d) > 0)) {
      add("transition-all", "warn", "transition: all on an interactive element", desc(el));
    }
  }

  const rootBg = getComputedStyle(root).backgroundColor;
  const bodyBg = getComputedStyle(document.body).backgroundColor;
  return {
    findings: [...out.values()],
    pageHeight,
    title: short(document.title),
    background: rgba(bodyBg)[3] > 0 ? bodyBg : rootBg,
  };
}
