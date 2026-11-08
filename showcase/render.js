// Renders one manifest item from the address alone, so a view can be shared or opened by a test.
// Query: item, theme, mode, density, type, bands, heads, images, reduced=1, content=long, spacers=0.
const q = new URLSearchParams(location.search);
const DATA = "/skills/ui-craft/assets/data/";
const KIT = "/skills/ui-craft/assets/kit/";
const json = async (url) => (await fetch(url)).json();

const LONG_WORD = "Donaudampfschifffahrtsgesellschaftskapitän";
const TEXT_PARENTS = "h1,h2,h3,p,li,a,button,dd,dt,span,label,blockquote,figcaption,td,th,summary";

function fail(message) {
  document.body.textContent = message;
  console.error(message);
}

function themeCss(theme, palette, fonts) {
  const block = (tokens) => Object.entries(tokens).map(([k, v]) => `--${k}:${v};`).join("");
  const families = [fonts.display, fonts.body];
  const faces = fonts.packages.map((pkg, i) => {
    const slug = pkg.split("/").pop();
    return `@font-face{font-family:"${families[i]} Variable";src:url(/showcase/fonts/${slug}-latin-wght-normal.woff2) format("woff2");font-weight:100 900;font-display:block}`;
  }).join("");
  return `${faces}:root{--font-display:"${fonts.display} Variable",ui-sans-serif,system-ui,sans-serif;--font-body:"${fonts.body} Variable",ui-sans-serif,system-ui,sans-serif;${block(palette.light)}}:root[data-theme="dark"]{${block(palette.dark)}}`;
}

function makeLong(doc) {
  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const parent = node.parentElement;
    const text = node.textContent.trim();
    if (text.length < 3 || !parent.matches(TEXT_PARENTS) || parent.closest("svg,script,style,.visually-hidden")) continue;
    node.textContent = parent.matches("h1,h2,h3") ? `${text} ${LONG_WORD} and a much longer line than anyone planned for` : `${text} ${text}`;
  }
}

async function main() {
  const [manifest, themes, palettes, fontData] = await Promise.all([json("manifest.json"), json("themes.json"), json(DATA + "palettes.json"), json(DATA + "fonts.json")]);
  const item = manifest.items.find((entry) => entry.id === q.get("item"));
  if (!item) return fail("No such item: " + q.get("item"));
  const theme = themes.themes.find((t) => t.id === q.get("theme")) || themes.themes[0];
  const palette = palettes.palettes.find((p) => p.id === theme.palette);
  const fonts = fontData.pairings.find((f) => f.id === theme.fonts);

  const file = new URL("/" + item.file, location.origin);
  const doc = new DOMParser().parseFromString(await (await fetch(file)).text(), "text/html");
  doc.querySelectorAll("[href],[src]").forEach((el) => {
    for (const name of ["href", "src"]) {
      const value = el.getAttribute(name);
      if (value && !value.startsWith("#") && !/^[a-z]+:/i.test(value)) el.setAttribute(name, new URL(value, file).pathname);
    }
  });

  const root = doc.documentElement;
  root.dataset.theme = q.get("mode") || theme.mode;
  root.dataset.radius = theme.radius;
  if (q.get("density")) root.dataset.density = q.get("density");
  for (const name of ["type", "bands", "heads", "images"]) if (q.get(name)) root.dataset[name] = q.get(name);
  if (q.get("spacers") === "0") doc.querySelectorAll(".sample-spacer").forEach((el) => el.remove());
  if (q.get("content") === "long") makeLong(doc);

  const reduced = q.get("reduced") === "1";
  const first = doc.createElement("script");
  first.textContent = `try{localStorage.removeItem("theme")}catch(e){}
${reduced ? 'const real=window.matchMedia.bind(window);window.matchMedia=(m)=>/prefers-reduced-motion:\\s*reduce/.test(m)?{matches:true,media:m,addEventListener(){},removeEventListener(){}}:real(m);' : ""}
addEventListener("load",()=>setTimeout(async()=>{await document.fonts.ready;await Promise.allSettled(document.getAnimations().filter((a)=>a instanceof CSSTransition).map((a)=>a.finished));document.documentElement.setAttribute("data-showcase-ready","")},60));`;
  doc.head.prepend(first);

  const direction = doc.createElement("link");
  direction.rel = "stylesheet";
  direction.href = KIT + "base/direction.css";
  const base = doc.head.querySelector('link[href$="base/base.css"]');
  if (base) base.after(direction); else doc.head.append(direction);

  const style = doc.createElement("style");
  style.textContent = themeCss(theme, palette, fonts) + (reduced
    ? "*,*::before,*::after{animation-duration:1ms!important;animation-delay:0ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important}[data-enter]{animation:none!important}"
    : "");
  doc.head.append(style);

  document.open();
  document.write("<!doctype html>" + root.outerHTML);
  document.close();
}

main().catch((error) => fail(String(error)));
