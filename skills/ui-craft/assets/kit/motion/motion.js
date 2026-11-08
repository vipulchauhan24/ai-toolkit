// Motion helpers for the kit. See references/motion/motion-sections.md for the attributes.
// Content is visible until this script decides to hide it, so a failed load hides nothing.
import { animate, inView, scroll, stagger } from "../vendor/motion.js";

const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const EASE = [0.22, 0.8, 0.3, 1];
const onScreen = (el) => el.getBoundingClientRect().top < window.innerHeight * 0.95;

function hide(els) {
  els.forEach((el) => { el.style.opacity = "0"; el.style.transform = "translateY(16px)"; });
}

function show(els, delay) {
  animate(els, { opacity: 1, transform: "none" }, { duration: 0.4, ease: EASE, delay });
}

function reveals() {
  document.querySelectorAll("[data-reveal]").forEach((el) => {
    if (onScreen(el)) return;
    hide([el]);
    inView(el, () => show([el]), { amount: 0.15 });
  });
  document.querySelectorAll("[data-reveal-group]").forEach((group) => {
    if (onScreen(group)) return;
    const items = [...group.children].slice(0, 6);
    hide(items);
    inView(group, () => show(items, stagger(0.05)), { amount: 0.1 });
  });
}

function counters() {
  document.querySelectorAll("[data-count]").forEach((el) => {
    const end = el.textContent;
    const match = end.match(/\d[\d,]*(?:\.\d+)?/);
    if (!match) return;
    const target = parseFloat(match[0].replace(/,/g, ""));
    const decimals = (match[0].split(".")[1] || "").length;
    const write = (value) => {
      const text = value.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
      el.textContent = end.replace(match[0], text);
    };
    inView(el, () => {
      const start = performance.now();
      const tick = (now) => {
        const t = Math.min((now - start) / 800, 1);
        write(target * (1 - Math.pow(1 - t, 3)));
        if (t < 1) requestAnimationFrame(tick);
        else el.textContent = end; // always ends on the exact original text
      };
      requestAnimationFrame(tick);
    });
  });
}

function timelines() {
  document.querySelectorAll("[data-timeline]").forEach((list) => {
    const line = list.querySelector(".timeline__progress");
    if (!line) return;
    line.hidden = false;
    scroll((progress) => { line.style.transform = `scaleY(${progress})`; }, { target: list, offset: ["start 75%", "end 60%"] });
  });
}

// One image drifting inside its frame. The script sets every transform, so with no script,
// or with reduced motion, the image simply sits still at its normal size.
function parallax() {
  const frame = document.querySelector("[data-parallax]");
  const media = frame && frame.querySelector("img, video");
  if (!media) return;
  const wide = window.matchMedia("(min-width: 768px)");
  const TRAVEL = 8; // percent of the frame's height, top to bottom
  const SCALE = 1.1; // leaves 5% spare at each edge, more than the 4% it moves either way
  let stop = null;
  const update = () => {
    if (stop) stop();
    stop = null;
    media.style.transform = "";
    if (!wide.matches) return;
    stop = scroll((progress) => {
      media.style.transform = `translateY(${((0.5 - progress) * TRAVEL).toFixed(2)}%) scale(${SCALE})`;
    }, { target: frame, offset: ["start end", "end start"] });
  };
  wide.addEventListener("change", update);
  update();
}

function nav() {
  document.querySelectorAll("[data-nav]").forEach((bar) => {
    const update = () => bar.classList.toggle("is-scrolled", window.scrollY > 8);
    update();
    window.addEventListener("scroll", update, { passive: true });

    const toggle = bar.querySelector(".nav__toggle");
    const sheet = bar.querySelector(".nav__sheet");
    if (!toggle || !sheet) return;
    const links = sheet.querySelectorAll("a");
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Close" : "Menu";
      document.documentElement.style.overflow = open ? "hidden" : "";
      if (open) {
        sheet.hidden = false;
        if (!still) {
          animate(sheet, { opacity: [0, 1] }, { duration: 0.25, ease: EASE });
          animate(links, { opacity: [0, 1], transform: ["translateY(8px)", "none"] }, { duration: 0.25, ease: EASE, delay: stagger(0.03) });
        }
      } else {
        sheet.hidden = true;
      }
    };
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    links.forEach((link) => link.addEventListener("click", () => setOpen(false)));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
  });
}

function forms() {
  document.querySelectorAll("form[data-form]").forEach((form) => {
    form.noValidate = true;
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      let first = null;
      form.querySelectorAll(".field").forEach((field) => {
        const input = field.querySelector("input, textarea, select");
        const error = field.querySelector(".field__error");
        if (!input || !error) return;
        const bad = !input.checkValidity();
        input.setAttribute("aria-invalid", String(bad));
        error.hidden = !bad;
        if (bad && !first) first = input;
      });
      if (first) { first.focus(); return; }
      const done = form.parentElement.querySelector(".form__success");
      if (done) { form.hidden = true; done.hidden = false; done.focus(); }
    });
  });
}

nav();
forms();
if (!still) {
  reveals();
  counters();
  timelines();
  parallax();
}
