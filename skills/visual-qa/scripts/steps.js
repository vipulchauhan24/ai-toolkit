// Body of one `playwright-cli run-code` call. capture.py wraps it in `async page => { ... }`
// and defines CONFIG and PAGE_CHECKS first. It returns plain JSON, images as base64.
const sleep = (ms) => page.waitForTimeout(ms);
const RISKY = /log-?out|sign-?out|delete|remove|unsubscribe|destroy/i;
const THEME_NAME = /theme|dark mode|light mode|^dark$|^light$/i;

const settle = async () => {
  try { await page.waitForLoadState("networkidle", { timeout: 5000 }); } catch (e) { /* a page that keeps polling */ }
  await page.evaluate(() => (document.fonts ? document.fonts.ready.then(() => 1) : 1));
  await sleep(400);
};

// Slow enough to watch, and it fires lazy images and scroll reveals before anything is measured.
const scrollThrough = async () => {
  const { height, view } = await page.evaluate(() => ({ height: document.documentElement.scrollHeight, view: window.innerHeight }));
  for (let y = 0; y < height; y += Math.round(view * 0.7)) {
    await page.evaluate((top) => window.scrollTo({ top, behavior: "instant" }), y);
    await sleep(CONFIG.scrollPause);
  }
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await sleep(600);
  await settle();
};

// Resizing a desktop browser leaves it a mouse device, so a phone width would not get
// pointer: coarse styles. Touch emulation turns those media queries on.
let touchCdp = null;
const setTouch = async (width) => {
  touchCdp = touchCdp || await page.context().newCDPSession(page);
  await touchCdp.send("Emulation.setTouchEmulationEnabled", { enabled: width <= 820 });
};

const capture = async (cdp, clip) => {
  const shot = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 85, captureBeyondViewport: true, clip });
  return shot.data;
};

// Tiles a model can read at a useful size: GRADE_WIDTH wide, at most TILE_HEIGHT tall.
const tiles = async (pageHeight, width) => {
  const scale = Math.min(1, CONFIG.gradeWidth / width);
  const cssHeight = Math.floor(CONFIG.tileHeight / scale);
  const cdp = await page.context().newCDPSession(page);
  const out = [];
  for (let y = 0; y < pageHeight && out.length < CONFIG.maxTiles; y += cssHeight) {
    out.push(await capture(cdp, { x: 0, y, width, height: Math.min(cssHeight, pageHeight - y), scale }));
  }
  await cdp.detach();
  return { images: out, truncated: pageHeight > cssHeight * CONFIG.maxTiles };
};

const listen = () => {
  const log = { console: [], failed: [] };
  const onConsole = (m) => { if (m.type() === "error" && log.console.length < 20) log.console.push(m.text().slice(0, 200)); };
  const onPageError = (e) => { if (log.console.length < 20) log.console.push(String(e).slice(0, 200)); };
  const onFailed = (r) => { if (log.failed.length < 20) log.failed.push(r.method() + " " + r.url().slice(0, 160) + " (" + (r.failure() || {}).errorText + ")"); };
  const onResponse = (r) => { if (r.status() >= 400 && log.failed.length < 20) log.failed.push(r.request().method() + " " + r.url().slice(0, 160) + " (" + r.status() + ")"); };
  page.on("console", onConsole);
  page.on("pageerror", onPageError);
  page.on("requestfailed", onFailed);
  page.on("response", onResponse);
  log.stop = () => {
    page.off("console", onConsole);
    page.off("pageerror", onPageError);
    page.off("requestfailed", onFailed);
    page.off("response", onResponse);
  };
  return log;
};

const finding = (id, severity, message, sample) => ({ id, severity, message, count: 1, samples: sample ? [sample] : [] });

const discover = async () => {
  await page.goto(CONFIG.base, { waitUntil: "load" });
  await settle();
  const routes = await page.evaluate((risky) => {
    const out = new Set([location.pathname]);
    for (const a of document.querySelectorAll("a[href]")) {
      const u = new URL(a.href, location.href);
      if (u.origin !== location.origin || new RegExp(risky, "i").test(u.pathname)) continue;
      if (/\.[a-z0-9]{2,5}$/i.test(u.pathname) && !/\.html?$/i.test(u.pathname)) continue;
      out.add(u.pathname);
    }
    return [...out];
  }, RISKY.source);
  const live = [];
  for (const route of routes) {
    const status = await page.request.get(new URL(route, CONFIG.base).href).then((r) => r.status()).catch(() => 0);
    if (status > 0 && status < 400) live.push(route);
  }
  return { routes: live };
};

const shot = async () => {
  const log = listen();
  await setTouch(CONFIG.width);
  await page.setViewportSize({ width: CONFIG.width, height: CONFIG.height });
  await page.emulateMedia({ colorScheme: CONFIG.theme, reducedMotion: "no-preference" });
  const response = await page.goto(CONFIG.url, { waitUntil: "load" });
  if (response && response.status() >= 400) throw new Error("the page returned " + response.status() + ": " + CONFIG.url);
  await settle();
  let themeVia = "preference";
  if (CONFIG.theme === "dark" && CONFIG.lightBackground) {
    const same = (await page.evaluate(PAGE_CHECKS)).background === CONFIG.lightBackground;
    if (same) {
      const toggle = page.getByRole("button", { name: THEME_NAME }).filter({ visible: true }).first();
      if (await toggle.count()) {
        await toggle.click({ timeout: 3000 }).catch(() => {});
        await sleep(500);
        themeVia = "toggle";
      } else {
        themeVia = "none";
      }
    }
  }
  await scrollThrough();
  const checks = await page.evaluate(PAGE_CHECKS);
  const width = await page.evaluate(() => document.documentElement.clientWidth);
  const captured = await tiles(checks.pageHeight, width);
  if (themeVia === "toggle") await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  log.stop();
  return { checks, tiles: captured.images, truncated: captured.truncated, themeVia, console: log.console, failed: log.failed };
};

const reduced = async () => {
  await setTouch(CONFIG.width);
  await page.setViewportSize({ width: CONFIG.width, height: CONFIG.height });
  await page.emulateMedia({ colorScheme: "light", reducedMotion: "reduce" });
  await page.goto(CONFIG.url, { waitUntil: "load" });
  await settle();
  const result = await page.evaluate(() => {
    const running = document.getAnimations().filter((a) => {
      const t = a.effect && a.effect.getComputedTiming();
      return a.playState === "running" && t && t.iterations === Infinity;
    });
    const hidden = [...document.body.querySelectorAll("h1,h2,h3,p,li,a,button")].filter((el) => {
      if (el.closest('[aria-hidden="true"],[hidden],[inert],dialog:not([open])')) return false;
      const s = getComputedStyle(el);
      if (s.display === "none" || s.visibility === "hidden" || !el.textContent.trim()) return false;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return false;
      for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
        if (getComputedStyle(n).position === "fixed") return false;
        if (parseFloat(getComputedStyle(n).opacity) < 0.05) return true;
      }
      return false;
    });
    return { running: running.length, hidden: hidden.length, sample: hidden[0] ? hidden[0].textContent.trim().slice(0, 60) : "" };
  });
  await page.emulateMedia({ reducedMotion: "no-preference" });
  const findings = [];
  if (result.hidden) findings.push(finding("reduced-hidden", "fail", "Content stays invisible under reduced motion until the page is scrolled (" + result.hidden + ")", result.sample));
  if (result.running) findings.push(finding("reduced-animating", "fail", "Endless animations keep running under reduced motion (" + result.running + ")"));
  return { findings };
};

const interact = async () => {
  const findings = [];
  const blocked = [];
  const guard = (route) => {
    if (route.request().method() === "GET" || route.request().method() === "HEAD") return route.continue();
    blocked.push(route.request().method() + " " + route.request().url().slice(0, 160));
    return route.abort();
  };
  await page.route("**/*", guard);
  await setTouch(1440);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.emulateMedia({ colorScheme: "light", reducedMotion: "no-preference" });
  await page.goto(CONFIG.url, { waitUntil: "load" });
  await settle();

  // Keyboard: walk the first stops and look for a visible focus style
  let stops = 0;
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Tab");
    await sleep(120);
    const state = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const s = getComputedStyle(el);
      const ring = (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== "none";
      return { ring, name: el.tagName.toLowerCase() + " " + (el.textContent || "").trim().slice(0, 40) };
    });
    if (!state) break;
    stops += 1;
    if (!state.ring) findings.push(finding("focus-visible", "fail", "Keyboard focus has no visible outline or ring", state.name));
  }
  if (!stops) findings.push(finding("keyboard", "fail", "Tab does not reach anything on the page"));

  // Links: request each one, then click it the way a visitor would
  const links = await page.evaluate(() => [...document.querySelectorAll("a[href]")].map((a) => ({
    raw: a.getAttribute("href"), url: a.href, external: new URL(a.href, location.href).origin !== location.origin,
  })));
  const checked = [];
  const external = [];
  for (const link of links) {
    if (link.raw.startsWith("mailto:") || link.raw.startsWith("tel:")) continue;
    if (link.external) { if (!external.includes(link.url)) external.push(link.url); continue; }
    if (CONFIG.seen.includes(link.url) || checked.includes(link.url) || RISKY.test(link.url) || checked.length >= CONFIG.maxLinks) continue;
    checked.push(link.url);
    if (link.raw.startsWith("#")) {
      if (link.raw.length > 1 && !(await page.evaluate((id) => !!document.getElementById(id), decodeURIComponent(link.raw.slice(1))))) {
        findings.push(finding("broken-anchor", "fail", "In-page link points at a section that does not exist", link.raw));
      }
      continue;
    }
    const status = await page.request.get(link.url).then((r) => r.status()).catch(() => 0);
    if (status === 0 || status >= 400) findings.push(finding("broken-link", "fail", "Link returns " + (status || "no response"), link.raw));
    const target = page.locator("a[href=" + JSON.stringify(link.raw) + "]").filter({ visible: true }).first();
    if (await target.count()) {
      await target.click({ timeout: 3000 }).catch(() => findings.push(finding("link-click", "warn", "A visitor cannot click this link", link.raw)));
      await sleep(350);
      await page.goto(CONFIG.url, { waitUntil: "load" });
      await settle();
    }
  }

  // Forms: submit empty, with every non-GET request blocked so nothing is really sent
  const formCount = Math.min(await page.locator("form").count(), 5);
  for (let i = 0; i < formCount; i++) {
    await page.goto(CONFIG.url, { waitUntil: "load" });
    await settle();
    const form = page.locator("form").nth(i);
    const submit = form.locator('button:not([type=button]):not([type=reset]), input[type=submit]').filter({ visible: true }).first();
    if (!(await submit.count())) continue;
    const before = blocked.length;
    const textBefore = await form.innerText();
    await submit.scrollIntoViewIfNeeded().catch(() => {});
    await submit.click({ timeout: 3000 }).catch(() => {});
    await sleep(700);
    const state = await form.evaluate((f) => ({
      invalid: !f.checkValidity() || f.querySelector('[aria-invalid="true"]') !== null,
      focusInside: f.contains(document.activeElement),
    })).catch(() => ({ invalid: false, focusInside: false }));
    const textAfter = await form.innerText().catch(() => textBefore);
    if (blocked.length > before) findings.push(finding("empty-submit", "fail", "An empty form tried to send a request", blocked[before]));
    else if (!state.invalid && textAfter === textBefore) findings.push(finding("form-feedback", "warn", "Submitting an empty form shows no message", "form " + (i + 1)));
  }

  // Phone menu
  await setTouch(390);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(CONFIG.url, { waitUntil: "load" });
  await settle();
  const navLinks = page.locator("header a, nav a").filter({ visible: true });
  const hiddenNav = (await page.locator("header a, nav a").count()) > 0 && (await navLinks.count()) <= 1;
  let menu = null;
  if (hiddenNav) {
    const button = page.locator("header button, nav button, [aria-controls], [aria-expanded]").filter({ visible: true }).filter({ hasNotText: /theme|dark|light/i }).first();
    if (await button.count()) {
      await button.click({ timeout: 3000 }).catch(() => {});
      await sleep(600);
      const opened = await page.locator("header a, nav a").filter({ visible: true }).count();
      if (opened <= 1) findings.push(finding("mobile-nav", "fail", "The phone menu button does not reveal the links"));
      const cdp = await page.context().newCDPSession(page);
      menu = await capture(cdp, { x: 0, y: 0, width: 390, height: 844, scale: 1 });
      await cdp.detach();
    } else {
      findings.push(finding("mobile-nav", "fail", "Navigation links are hidden on phones with no button to open them"));
    }
  }

  await page.unroute("**/*", guard);
  return { findings, checked, external, stops, menu };
};

const STEPS = { discover, shot, reduced, interact };
return await STEPS[CONFIG.step]();
