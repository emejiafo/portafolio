"""Public profile and portfolio frontend (Phase 2)."""

import html
import os
from typing import Any, Dict, List, Optional

import gradio as gr
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
PUBLIC_API_BASE_URL = os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8000")
HTTP_TIMEOUT = 15.0
DEFAULT_SKY_IMAGE_PATHS = "/uploads/assets/sky/mountain-sky-1.jpg,/uploads/assets/sky/mountain-sky-2.jpg"


CUSTOM_CSS = """
:root {
    --bg-top: #f5f2ea;
    --bg-bottom: #efe8da;
    --bg-blob-a: rgba(247, 231, 206, 1);
    --bg-blob-b: rgba(205, 233, 229, 1);

    --surface: #fffdf7;
    --surface-soft: #f6f2e8;
    --surface-contrast: #ffffff;

    --ink: #1f2a24;
    --muted: #59665f;

    --accent: #0f766e;
    --accent-ink: #f6fbf9;
    --accent-soft-bg: #e7f2f0;
    --accent-soft-ink: #21554d;

    --warning-bg: #f59e0b;
    --warning-ink: #1e1605;

    --line: #d8d2c2;
    --line-strong: #c8bea8;
    --chip-line: rgba(15, 118, 110, 0.36);
    --chip-bg: rgba(15, 118, 110, 0.09);
    --chip-ink: #0f5e57;

    --hero-start: #102420;
    --hero-mid: #1f4139;
    --hero-end: #27564b;
    --hero-text: #f8f7f4;
    --hero-subtext: rgba(250, 248, 242, 0.92);
    --hero-border: rgba(255, 255, 255, 0.2);
    --hero-glow: rgba(255, 184, 108, 0.85);
    --hero-photo-fade: rgba(6, 30, 49, 0.58);
    --hero-photo-url: none;
    --hero-photo-url-secondary: none;

    --page-photo-url: none;
    --page-photo-url-profile: none;
    --page-photo-url-projects: none;
    --page-photo-url-contact: none;
    --page-photo-opacity: 0.26;
    --page-photo-vignette: rgba(7, 26, 43, 0.54);

    --card-shadow: rgba(32, 45, 39, 0.07);
    --hero-shadow: rgba(10, 28, 25, 0.22);

    --control-bg: #fffef9;
    --control-ink: #1f2a24;
    --control-line: #cfc7b5;
    --control-focus: rgba(15, 118, 110, 0.32);

    --status-bg: #f8f4eb;
    --status-line: #d4ccb7;
    --status-success-bg: #e9f5ef;
    --status-success-line: #8fc7ad;
    --status-success-ink: #17583a;
    --status-error-bg: #faece8;
    --status-error-line: #e5b5a8;
    --status-error-ink: #8b2f23;
}

:root[data-theme="dark"] {
    --bg-top: #0f1715;
    --bg-bottom: #111d1a;
    --bg-blob-a: rgba(28, 53, 48, 0.88);
    --bg-blob-b: rgba(15, 43, 49, 0.75);

    --surface: #17211e;
    --surface-soft: #121d1a;
    --surface-contrast: #1b2824;

    --ink: #e3efe9;
    --muted: #a4b8ae;

    --accent: #2ab3a8;
    --accent-ink: #042623;
    --accent-soft-bg: #1d3632;
    --accent-soft-ink: #a8e8df;

    --warning-bg: #d18e25;
    --warning-ink: #221603;

    --line: #2f4a43;
    --line-strong: #426259;
    --chip-line: rgba(42, 179, 168, 0.52);
    --chip-bg: rgba(42, 179, 168, 0.14);
    --chip-ink: #9de0d8;

    --hero-start: #10211e;
    --hero-mid: #17342d;
    --hero-end: #1a453d;
    --hero-text: #f0f7f4;
    --hero-subtext: rgba(225, 241, 235, 0.9);
    --hero-border: rgba(167, 214, 205, 0.2);
    --hero-glow: rgba(255, 188, 88, 0.58);
    --hero-photo-fade: rgba(4, 18, 31, 0.68);

    --page-photo-opacity: 0.34;
    --page-photo-vignette: rgba(4, 15, 27, 0.72);

    --card-shadow: rgba(3, 8, 7, 0.46);
    --hero-shadow: rgba(2, 11, 9, 0.62);

    --control-bg: #14211d;
    --control-ink: #e3efe9;
    --control-line: #33524a;
    --control-focus: rgba(42, 179, 168, 0.42);

    --status-bg: #182722;
    --status-line: #2d4a41;
    --status-success-bg: #133026;
    --status-success-line: #2d7b5b;
    --status-success-ink: #8be2b8;
    --status-error-bg: #331d1a;
    --status-error-line: #87403a;
    --status-error-ink: #ffb9ad;
}

body,
.gradio-container {
    font-family: "Space Grotesk", sans-serif;
    background:
        radial-gradient(circle at 10% 15%, var(--bg-blob-a) 0%, transparent 36%),
        radial-gradient(circle at 90% 12%, var(--bg-blob-b) 0%, transparent 28%),
        linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
    color: var(--ink);
}

body {
    overflow-x: hidden;
}

.gradio-container {
    position: relative;
    isolation: isolate;
}

.gradio-container::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    background-image:
        linear-gradient(
            180deg,
            var(--page-photo-vignette) 0%,
            rgba(9, 27, 44, 0.16) 27%,
            rgba(9, 27, 44, 0) 64%
        ),
        var(--page-photo-url, none);
    background-size: cover;
    background-position: center 12%;
    opacity: var(--page-photo-opacity);
    transform: scale(1.04);
    filter: saturate(1.14) contrast(1.06);
    transition: opacity 320ms ease, filter 320ms ease;
}

:root.page-bg-swapping .gradio-container::before {
    opacity: 0.08;
    filter: saturate(1.02) contrast(1.01);
}

.gradio-container,
.gradio-container * {
    transition: background-color 170ms ease, border-color 170ms ease, color 170ms ease, box-shadow 220ms ease;
}

a {
    color: var(--accent);
}

a:hover {
    color: var(--accent-soft-ink);
}

.hero-shell {
    background: linear-gradient(135deg, var(--hero-start) 0%, var(--hero-mid) 55%, var(--hero-end) 100%);
    margin-top: -10px;
    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    width: 100vw;
    min-height: clamp(370px, 62vh, 760px);
    border: none;
    border-radius: 0;
    padding: clamp(26px, 5.5vw, 74px) clamp(18px, 7vw, 90px) clamp(26px, 7.5vh, 78px);
    color: var(--hero-text);
    box-shadow: inset 0 -130px 180px rgba(4, 15, 25, 0.46), 0 24px 55px var(--hero-shadow);
    overflow: hidden;
    position: relative;
    display: flex;
    align-items: flex-end;
}

.hero-shell::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(circle at 78% 22%, rgba(255, 207, 138, 0.42) 0%, rgba(255, 207, 138, 0) 30%),
        linear-gradient(180deg, rgba(5, 15, 24, 0.16) 8%, rgba(6, 26, 43, 0.62) 100%),
        linear-gradient(110deg, rgba(255, 255, 255, 0.14), rgba(255, 255, 255, 0) 44%),
        var(--hero-photo-url-secondary, var(--hero-photo-url, none)),
        var(--hero-photo-url, none);
    background-size: cover;
    background-position: center 16%, center, left top, center 42%, center 52%;
    opacity: 0.97;
    transform: scale(1.03);
    filter: saturate(1.22) contrast(1.08);
    animation: cinematic-pan 22s ease-in-out infinite alternate;
    pointer-events: none;
}

.hero-shell::after {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 84% 17%, var(--hero-glow) 0%, rgba(255, 184, 108, 0) 36%),
        linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0) 42%, rgba(4, 13, 21, 0.46) 100%);
    mix-blend-mode: screen;
    opacity: 0.62;
    z-index: 1;
    pointer-events: none;
}

.hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 18px;
    flex-wrap: wrap;
    position: relative;
    z-index: 2;
    width: min(1140px, 100%);
    margin: 0 auto;
    padding: clamp(14px, 2.4vw, 24px);
    border: 1px solid var(--hero-border);
    border-radius: 18px;
    backdrop-filter: blur(7px);
    background: linear-gradient(120deg, rgba(8, 20, 32, 0.58), rgba(9, 24, 37, 0.32));
    box-shadow: 0 14px 34px rgba(2, 10, 18, 0.28);
}

.hero-copy {
    flex: 1;
    min-width: 220px;
    max-width: 860px;
}

.hero-kicker {
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.75rem;
    color: rgba(240, 251, 248, 0.88);
}

.hero-title {
    margin: 8px 0 0;
    font-size: clamp(2rem, 5vw, 4rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    text-wrap: balance;
    text-shadow: 0 10px 22px rgba(3, 11, 19, 0.45);
}

.hero-subtitle {
    margin: 12px 0 0;
    max-width: 760px;
    color: var(--hero-subtext);
    font-size: clamp(1rem, 1.45vw, 1.18rem);
    line-height: 1.45;
}

.hero-badges {
    margin-top: 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.hero-badge {
    border: 1px solid rgba(213, 234, 255, 0.38);
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 0.8rem;
    color: #edf7ff;
    background: rgba(16, 47, 75, 0.34);
}

.theme-toggle {
    border: 1px solid rgba(235, 245, 255, 0.48);
    border-radius: 999px;
    background: rgba(9, 28, 44, 0.44);
    color: var(--hero-text);
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 7px 14px;
    cursor: pointer;
}

.theme-toggle:hover {
    background: rgba(9, 33, 54, 0.72);
    transform: translateY(-1px);
}

.theme-toggle:focus-visible {
    outline: 2px solid rgba(255, 255, 255, 0.78);
    outline-offset: 2px;
}

.tab-shell {
    margin-top: 14px;
}

.portfolio-panel {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 10px 24px var(--card-shadow);
    animation: rise-in 420ms ease;
}

.section-title {
    margin: 0 0 10px;
    font-size: 1.2rem;
    font-weight: 700;
}

.meta-line {
    color: var(--muted);
    font-size: 0.93rem;
    margin-bottom: 10px;
}

.skill-row,
.tech-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.skill-chip,
.tech-chip {
    border: 1px solid var(--chip-line);
    border-radius: 999px;
    padding: 4px 10px;
    background: var(--chip-bg);
    color: var(--chip-ink);
    font-size: 0.84rem;
}

.contact-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 12px;
}

.contact-row a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
}

.contact-row a:hover {
    text-decoration: underline;
}

.cv-shell {
    background: var(--surface-soft);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px;
}

.sky-panel {
    margin-top: 14px;
}

.sky-intro {
    margin: 0 0 10px;
}

.sky-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
}

.sky-card {
    margin: 0;
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    background: var(--surface-soft);
    aspect-ratio: 16 / 9;
    box-shadow: 0 10px 24px var(--card-shadow);
}

.sky-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: saturate(1.15) contrast(1.02);
}

.sky-card.is-missing {
    display: none;
}

.sky-note {
    margin-top: 10px;
    font-size: 0.84rem;
    color: var(--muted);
}

.cv-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.cv-frame {
    width: 100%;
    min-height: 540px;
    border: 1px solid var(--line-strong);
    border-radius: 12px;
    margin-top: 10px;
    background: var(--surface-contrast);
}

.cta-btn,
.project-link {
    display: inline-block;
    border-radius: 999px;
    border: 1px solid transparent;
    text-decoration: none;
    padding: 6px 14px;
    font-weight: 600;
    margin-right: 8px;
}

.cta-btn {
    background: var(--accent);
    color: var(--accent-ink);
}

.project-link.live {
    background: var(--warning-bg);
    color: var(--warning-ink);
}

.project-link.code {
    border-color: var(--chip-line);
    color: var(--accent-soft-ink);
    background: var(--accent-soft-bg);
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.project-card {
    background: var(--surface-contrast);
    border: 1px solid var(--line);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 8px 22px var(--card-shadow);
}

.project-cover {
    width: 100%;
    aspect-ratio: 16 / 8;
    object-fit: cover;
    background: var(--surface-soft);
}

.project-body {
    padding: 12px;
}

.project-title {
    margin: 0;
    font-weight: 700;
    font-size: 1.08rem;
}

.project-type {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.78rem;
    color: var(--muted);
}

.project-desc {
    margin: 8px 0;
    color: var(--ink);
    font-size: 0.95rem;
}

.assets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
    margin-top: 12px;
}

.assets-grid img {
    width: 100%;
    border-radius: 10px;
    border: 1px solid var(--line);
    aspect-ratio: 16 / 10;
    object-fit: cover;
}

.status-msg {
    border-radius: 12px;
    padding: 12px 14px;
    border: 1px solid var(--status-line);
    background: var(--status-bg);
}

.status-msg.success {
    background: var(--status-success-bg);
    border-color: var(--status-success-line);
    color: var(--status-success-ink);
}

.status-msg.error {
    background: var(--status-error-bg);
    border-color: var(--status-error-line);
    color: var(--status-error-ink);
}

.gradio-container [role="tablist"] {
    gap: 8px;
    margin-bottom: 12px;
}

.gradio-container [role="tab"] {
    border: 1px solid var(--line) !important;
    background: var(--surface-soft) !important;
    color: var(--muted) !important;
    border-radius: 10px !important;
}

.gradio-container [role="tab"][aria-selected="true"] {
    background: var(--accent-soft-bg) !important;
    color: var(--accent-soft-ink) !important;
    border-color: var(--chip-line) !important;
}

.gradio-container label {
    color: var(--ink) !important;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container select,
.gradio-container [role="combobox"],
.gradio-container [role="textbox"] {
    background: var(--control-bg) !important;
    color: var(--control-ink) !important;
    border-color: var(--control-line) !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus,
.gradio-container select:focus,
.gradio-container [role="combobox"]:focus,
.gradio-container [role="textbox"]:focus {
    box-shadow: 0 0 0 2px var(--control-focus) !important;
}

.gradio-container input::placeholder,
.gradio-container textarea::placeholder {
    color: var(--muted) !important;
}

.gradio-container button {
    border-color: var(--control-line) !important;
    color: var(--ink) !important;
    background: var(--surface-soft) !important;
}

.gradio-container button.primary {
    background: var(--accent) !important;
    color: var(--accent-ink) !important;
    border-color: transparent !important;
}

.gradio-container footer,
.gradio-container [data-testid="footer"] {
    color: var(--muted) !important;
}

[role="listbox"] {
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
}

[role="option"] {
    color: var(--ink) !important;
}

[role="option"][aria-selected="true"] {
    background: var(--accent-soft-bg) !important;
    color: var(--accent-soft-ink) !important;
}

.portfolio-panel.theme-light {
    background: #fffdf7 !important;
    border: 1px solid #d8d2c2 !important;
    color: #1f2a24 !important;
}

.portfolio-panel.theme-dark {
    background: #17211e !important;
    border: 1px solid #2f4a43 !important;
    color: #e3efe9 !important;
}

[role="tab"].theme-tab-light {
    background: #f6f2e8 !important;
    border: 1px solid #d8d2c2 !important;
    color: #59665f !important;
}

[role="tab"].theme-tab-light-selected {
    background: #e7f2f0 !important;
    border: 1px solid rgba(15, 118, 110, 0.36) !important;
    color: #21554d !important;
}

[role="tab"].theme-tab-dark {
    background: #121d1a !important;
    border: 1px solid #2f4a43 !important;
    color: #a4b8ae !important;
}

[role="tab"].theme-tab-dark-selected {
    background: #1d3632 !important;
    border: 1px solid rgba(42, 179, 168, 0.52) !important;
    color: #a8e8df !important;
}

.mono {
    font-family: "IBM Plex Mono", monospace;
}

@keyframes rise-in {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes cinematic-pan {
    from {
        transform: scale(1.03) translate3d(0, 0, 0);
    }
    to {
        transform: scale(1.08) translate3d(-2.5%, -1.4%, 0);
    }
}

@media (max-width: 900px) {
    .hero-shell {
        min-height: 420px;
        padding: 16px 14px 20px;
    }

    .hero-top {
        align-items: flex-start;
        border-radius: 14px;
    }

    .hero-title {
        font-size: clamp(1.65rem, 8vw, 2.6rem);
    }

    .hero-subtitle {
        font-size: 0.98rem;
    }

    .projects-grid {
        grid-template-columns: 1fr;
    }

    .cv-frame {
        min-height: 380px;
    }
}
"""


THEME_HEAD_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
    href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap"
    rel="stylesheet"
/>
<script>
(() => {
  const THEME_KEY = "portfolio-theme";
  const DARK = "dark";
  const LIGHT = "light";
  const root = document.documentElement;
  const media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  const getSavedTheme = () => {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (_error) {
      return null;
    }
  };

  const setSavedTheme = (theme) => {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_error) {
      // Storage can be blocked in privacy modes.
    }
  };

    const toCssValue = (value) => (value || "").trim();

    const resolveTabImage = (tabLabel) => {
        const name = (tabLabel || "").trim().toLowerCase();
        const styles = getComputedStyle(root);
        const profile = toCssValue(styles.getPropertyValue("--page-photo-url-profile"));
        const projects = toCssValue(styles.getPropertyValue("--page-photo-url-projects"));
        const contact = toCssValue(styles.getPropertyValue("--page-photo-url-contact"));

        if (name.includes("project")) {
            return projects || profile;
        }
        if (name.includes("contact")) {
            return contact || projects || profile;
        }
        return profile || projects || contact;
    };

    const syncTabBackground = () => {
        const selectedTab = document.querySelector('.gradio-container [role="tab"][aria-selected="true"]');
        if (!selectedTab) {
            return;
        }

        const nextImage = resolveTabImage(selectedTab.textContent || "");
        if (!nextImage) {
            return;
        }

        const currentImage = toCssValue(getComputedStyle(root).getPropertyValue("--page-photo-url"));
        if (nextImage === currentImage) {
            return;
        }

        root.classList.add("page-bg-swapping");
        window.setTimeout(() => {
            root.style.setProperty("--page-photo-url", nextImage);
            window.requestAnimationFrame(() => {
                root.classList.remove("page-bg-swapping");
            });
        }, 120);
    };

    const bindTabBackgroundSync = () => {
        document.querySelectorAll('.gradio-container [role="tab"]').forEach((tab) => {
            if (tab.dataset.bgBound === "true") {
                return;
            }
            tab.dataset.bgBound = "true";
            tab.addEventListener("click", () => {
                window.setTimeout(syncTabBackground, 40);
            });
            tab.addEventListener("keydown", () => {
                window.setTimeout(syncTabBackground, 40);
            });
        });
    };

  const updateToggle = (theme) => {
    const button = document.getElementById("theme-toggle");
    if (!button) {
      return;
    }
    const isDark = theme === DARK;
    button.textContent = isDark ? "Light mode" : "Dark mode";
    button.setAttribute("aria-pressed", isDark ? "true" : "false");
  };

    const syncThemeTargets = (theme) => {
        const targets = document.querySelectorAll(
            ".gradio-container .main, .gradio-container .contain, .gradio-container .wrap, .gradio-container .tabs"
        );
        targets.forEach((target) => {
            target.setAttribute("data-portfolio-theme", theme);
        });
    };

    const syncBodyMode = (theme) => {
        if (!document.body) {
            return;
        }
        const isDark = theme === DARK;
        document.body.classList.toggle("dark", isDark);
        document.body.classList.toggle("light", !isDark);
    };

    const applyInlineTheme = (theme) => {
        const isDark = theme === DARK;

        const palette = {
            panelBg: isDark ? "#17211e" : "#fffdf7",
            panelBorder: isDark ? "#2f4a43" : "#d8d2c2",
            panelInk: isDark ? "#e3efe9" : "#1f2a24",
            muted: isDark ? "#a4b8ae" : "#59665f",
            tabBg: isDark ? "#121d1a" : "#f6f2e8",
            tabBorder: isDark ? "#2f4a43" : "#d8d2c2",
            tabInk: isDark ? "#a4b8ae" : "#59665f",
            tabSelBg: isDark ? "#1d3632" : "#e7f2f0",
            tabSelBorder: isDark ? "rgba(42, 179, 168, 0.52)" : "rgba(15, 118, 110, 0.36)",
            tabSelInk: isDark ? "#a8e8df" : "#21554d",
            cardBg: isDark ? "#1b2824" : "#ffffff",
            shellBg: isDark ? "#121d1a" : "#f6f2e8",
            frameBg: isDark ? "#0f1715" : "#ffffff",
            frameBorder: isDark ? "#426259" : "#c8bea8",
            statusBg: isDark ? "#182722" : "#f8f4eb",
            statusBorder: isDark ? "#2d4a41" : "#d4ccb7",
            statusInk: isDark ? "#d7e8e0" : "#1f2a24",
            chipBg: isDark ? "rgba(42, 179, 168, 0.14)" : "rgba(15, 118, 110, 0.09)",
            chipBorder: isDark ? "rgba(42, 179, 168, 0.52)" : "rgba(15, 118, 110, 0.36)",
            chipInk: isDark ? "#9de0d8" : "#0f5e57",
            inputBg: isDark ? "#17211e" : "#fffdf7",
            inputBorder: isDark ? "#33524a" : "#cfc7b5",
            inputInk: isDark ? "#e3efe9" : "#1f2a24",
        };

        const setStyles = (selector, declarations) => {
            document.querySelectorAll(selector).forEach((el) => {
                Object.entries(declarations).forEach(([name, value]) => {
                    el.style.setProperty(name, value, "important");
                });
            });
        };

        document.querySelectorAll("section.portfolio-panel").forEach((panel) => {
            panel.classList.remove("theme-light", "theme-dark");
            panel.classList.add(isDark ? "theme-dark" : "theme-light");
        });

        setStyles(".project-card", {
            background: palette.cardBg,
            border: `1px solid ${palette.panelBorder}`,
        });
        setStyles(".cv-shell", {
            background: palette.shellBg,
            border: `1px solid ${palette.panelBorder}`,
        });
        setStyles(".cv-frame", {
            background: palette.frameBg,
            border: `1px solid ${palette.frameBorder}`,
        });
        setStyles(".meta-line, .project-type", { color: palette.muted });
        setStyles(".project-desc", { color: palette.panelInk });
        setStyles(".skill-chip, .tech-chip", {
            background: palette.chipBg,
            border: `1px solid ${palette.chipBorder}`,
            color: palette.chipInk,
        });
        setStyles(".status-msg", {
            background: palette.statusBg,
            border: `1px solid ${palette.statusBorder}`,
            color: palette.statusInk,
        });
        setStyles(".status-msg.success", {
            background: isDark ? "#133026" : "#e9f5ef",
            border: `1px solid ${isDark ? "#2d7b5b" : "#8fc7ad"}`,
            color: isDark ? "#8be2b8" : "#17583a",
        });
        setStyles(".status-msg.error", {
            background: isDark ? "#331d1a" : "#faece8",
            border: `1px solid ${isDark ? "#87403a" : "#e5b5a8"}`,
            color: isDark ? "#ffb9ad" : "#8b2f23",
        });
        setStyles("input, textarea, select", {
            "background-color": palette.inputBg,
            "border-color": palette.inputBorder,
            color: palette.inputInk,
        });

        document.querySelectorAll('[role="tab"]').forEach((tab) => {
            tab.classList.remove(
                "theme-tab-light",
                "theme-tab-light-selected",
                "theme-tab-dark",
                "theme-tab-dark-selected"
            );

            const selected = tab.getAttribute("aria-selected") === "true";

            if (isDark) {
                tab.classList.add(selected ? "theme-tab-dark-selected" : "theme-tab-dark");
            } else {
                tab.classList.add(selected ? "theme-tab-light-selected" : "theme-tab-light");
            }
        });
    };

  const applyTheme = (theme) => {
    const normalized = theme === DARK ? DARK : LIGHT;
    root.setAttribute("data-theme", normalized);
        syncThemeTargets(normalized);
        syncBodyMode(normalized);
        applyInlineTheme(normalized);
    updateToggle(normalized);
  };

  const initialTheme = () => {
    const saved = getSavedTheme();
    if (saved === DARK || saved === LIGHT) {
      return saved;
    }
    return media && media.matches ? DARK : LIGHT;
  };

  const bindThemeToggle = () => {
    const button = document.getElementById("theme-toggle");
    if (!button || button.dataset.bound === "true") {
      return;
    }

    button.dataset.bound = "true";
    button.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") === DARK ? DARK : LIGHT;
      const next = current === DARK ? LIGHT : DARK;
      applyTheme(next);
      setSavedTheme(next);
    });

    updateToggle(root.getAttribute("data-theme"));
  };

  applyTheme(initialTheme());
    syncTabBackground();

  if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            bindThemeToggle();
            bindTabBackgroundSync();
            syncTabBackground();
        });
  } else {
    bindThemeToggle();
        bindTabBackgroundSync();
        syncTabBackground();
  }

  const observeBody = () => {
        if (!document.body) {
            return;
    }

        const observer = new MutationObserver(() => {
            bindThemeToggle();
            bindTabBackgroundSync();
            const activeTheme = root.getAttribute("data-theme") === DARK ? DARK : LIGHT;
            syncThemeTargets(activeTheme);
            syncBodyMode(activeTheme);
            applyInlineTheme(activeTheme);
            syncTabBackground();
        });

        observer.observe(document.body, { childList: true, subtree: true });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", observeBody);
  } else {
    observeBody();
  }

  if (media && typeof media.addEventListener === "function") {
    media.addEventListener("change", (event) => {
      if (getSavedTheme()) {
        return;
      }
      applyTheme(event.matches ? DARK : LIGHT);
    });
  }
})();
</script>
"""


def _join_public_url(path: Optional[str]) -> Optional[str]:
    """Build a browser-reachable URL for uploaded/static content."""
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if path.startswith("/"):
        return f"{PUBLIC_API_BASE_URL.rstrip('/')}{path}"
    return f"{PUBLIC_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def _parse_csv_items(value: str) -> List[str]:
    """Split a comma-separated env var into de-duplicated items."""
    items: List[str] = []
    for raw in (value or "").split(","):
        cleaned = raw.strip()
        if cleaned and cleaned not in items:
            items.append(cleaned)
    return items


def _configured_sky_images() -> List[str]:
    """Return configured decorative sky photos for the profile page."""
    return _parse_csv_items(os.getenv("PORTFOLIO_SKY_IMAGES", DEFAULT_SKY_IMAGE_PATHS))


def _css_url(value: Optional[str]) -> str:
    """Convert a URL into a CSS url(...) literal or none."""
    if not value:
        return "none"
    return f"url('{_escape(value)}')"


def render_sky_style_vars(sky_images: List[str]) -> str:
    """Expose sky image URLs as root CSS variables for hero and page background."""
    profile_url = _join_public_url(sky_images[0]) if sky_images else None

    projects_url = profile_url
    if len(sky_images) > 1:
        second_candidate = _join_public_url(sky_images[1])
        if second_candidate:
            projects_url = second_candidate

    contact_url = projects_url or profile_url
    if len(sky_images) > 2:
        third_candidate = _join_public_url(sky_images[2])
        if third_candidate:
            contact_url = third_candidate

    hero_secondary_url = projects_url or profile_url
    if len(sky_images) > 3:
        fourth_candidate = _join_public_url(sky_images[3])
        if fourth_candidate:
            hero_secondary_url = fourth_candidate

    return f"""
    <style>
      :root {{
        --hero-photo-url: {_css_url(profile_url)};
        --hero-photo-url-secondary: {_css_url(hero_secondary_url)};

        --page-photo-url-profile: {_css_url(profile_url)};
        --page-photo-url-projects: {_css_url(projects_url)};
        --page-photo-url-contact: {_css_url(contact_url)};
        --page-photo-url: {_css_url(profile_url)};
      }}
    </style>
    """


def render_hero_header(sky_images: List[str]) -> str:
    """Render hero section with optional mountain sky background."""
    return f"""
            <header class='hero-shell'>
                            <div class='hero-top'>
                                <div class='hero-copy'>
                                    <p class='hero-kicker'>Mountain Light Series</p>
                                    <h1 class='hero-title'>Public Profile and Portfolio</h1>
                                    <p class='hero-subtitle'>
                                        Cinematic project stories at the intersection of machine learning,
                                        data engineering, and real-world product impact.
                                    </p>
                                    <div class='hero-badges'>
                                        <span class='hero-badge'>Machine Learning</span>
                                        <span class='hero-badge'>Data Platforms</span>
                                        <span class='hero-badge'>AI Integrations</span>
                                    </div>
                                </div>
                                <button id='theme-toggle' class='theme-toggle' type='button' aria-label='Toggle dark mode' aria-pressed='false'>
                                    Dark mode
                                </button>
                            </div>
            </header>
    """


def render_sky_panel(sky_images: List[str]) -> str:
    """Render decorative image strip for custom mountain sky photos."""
    if not sky_images:
        return """
        <section class='portfolio-panel sky-panel'>
          <h3 class='section-title'>Sky Visuals</h3>
          <p class='meta-line'>
            Add photos under <span class='mono'>data/uploads/assets/sky/</span> and set
            <span class='mono'>PORTFOLIO_SKY_IMAGES</span> with comma-separated
            <span class='mono'>/uploads/...</span> paths.
          </p>
        </section>
        """

    sky_cards: List[str] = []
    for index, image_path in enumerate(sky_images[:4], start=1):
        image_url = _join_public_url(image_path)
        if not image_url:
            continue
        sky_cards.append(
            f"""
            <figure class='sky-card'>
              <img src='{_escape(image_url)}' alt='Mountain sky frame {index}' loading='lazy'
                   onerror=\"this.closest('.sky-card').classList.add('is-missing');\" />
            </figure>
            """
        )

    if not sky_cards:
        return """
        <section class='portfolio-panel sky-panel'>
          <h3 class='section-title'>Sky Visuals</h3>
          <p class='meta-line'>No valid sky image URLs are configured yet.</p>
        </section>
        """

    return f"""
    <section class='portfolio-panel sky-panel'>
      <h3 class='section-title'>Sky Visuals</h3>
      <p class='meta-line sky-intro'>
        Your mountain sky photos can set the mood and make the page feel more personal.
      </p>
      <div class='sky-grid'>
        {''.join(sky_cards)}
      </div>
      <p class='sky-note'>
        Tip: store originals in <span class='mono'>data/uploads/assets/sky/</span> and reference them as
        <span class='mono'>/uploads/assets/sky/your-file.jpg</span> in <span class='mono'>PORTFOLIO_SKY_IMAGES</span>.
      </p>
    </section>
    """


async def api_get_public(endpoint: str, params: Optional[Dict[str, str]] = None) -> Optional[Any]:
    """GET helper for the public API namespace."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(f"{API_BASE_URL}/api/public{endpoint}", params=params)
            if response.status_code == 200:
                return response.json()
            print(f"Public API GET error {response.status_code}: {response.text}")
    except Exception as exc:
        print(f"Error fetching public endpoint {endpoint}: {exc}")
    return None


async def api_post_public(endpoint: str, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
    """POST helper for the public API namespace."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
            response = await client.post(f"{API_BASE_URL}/api/public{endpoint}", json=data)
            try:
                payload = response.json()
            except Exception:
                payload = {"detail": response.text}
            return response.status_code, payload
    except Exception as exc:
        return 0, {"detail": str(exc)}


def _escape(value: Optional[str]) -> str:
    return html.escape(value or "", quote=True)


def render_profile_card(profile: Dict[str, Any]) -> str:
    """Render profile summary panel."""
    name = _escape(profile.get("full_name") or "Portfolio Owner")
    title = _escape(profile.get("professional_title") or "Independent Builder")
    bio = _escape(profile.get("bio_short") or "Building data and software products.")
    location = _escape(profile.get("location") or "")
    email = _escape(profile.get("email") or "")

    skills = profile.get("skills") or []
    skill_html = "".join(f"<span class='skill-chip'>{_escape(skill)}</span>" for skill in skills)
    if not skill_html:
        skill_html = "<span class='meta-line'>Skills will be listed soon.</span>"

    links = []
    for label, key in [
        ("Website", "website_url"),
        ("LinkedIn", "linkedin_url"),
        ("GitHub", "github_url"),
    ]:
        url = profile.get(key)
        if url:
            safe_url = _escape(url)
            links.append(f"<a href='{safe_url}' target='_blank' rel='noopener'>{label}</a>")
    links_html = " ".join(links) if links else "<span class='meta-line'>Social links coming soon.</span>"

    location_line = f"<div class='meta-line'>Based in {location}</div>" if location else ""
    email_line = f"<div class='meta-line'>Email: <span class='mono'>{email}</span></div>" if email else ""

    return f"""
        <section class="portfolio-panel">
      <h2 class="section-title">{name}</h2>
      <div class="meta-line">{title}</div>
      {location_line}
      {email_line}
      <p>{bio}</p>
      <div class="skill-row">{skill_html}</div>
      <div class="contact-row">{links_html}</div>
    </section>
    """


def render_cv_panel(profile: Dict[str, Any]) -> str:
    """Render CV embed panel with fallback link."""
    cv_url = _join_public_url(profile.get("cv_url"))
    cv_label = _escape(profile.get("cv_label") or "Open CV")
    cv_updated_at = _escape(profile.get("cv_updated_at") or "")

    if not cv_url:
        return """
        <section class="cv-shell">
          <div class="status-msg">CV metadata is not configured yet.</div>
        </section>
        """

    safe_cv_url = _escape(cv_url)
    updated_badge = f"<span class='meta-line'>Updated: {cv_updated_at}</span>" if cv_updated_at else ""

    return f"""
    <section class="cv-shell">
      <div class="cv-header">
        <a class="cta-btn" href="{safe_cv_url}" target="_blank" rel="noopener">{cv_label}</a>
        {updated_badge}
      </div>
      <iframe class="cv-frame" src="{safe_cv_url}#toolbar=0"></iframe>
      <p class="meta-line">If the embedded viewer fails, use the button above to open the CV in a new tab.</p>
    </section>
    """


def _pick_cover(project: Dict[str, Any]) -> Optional[str]:
    assets = project.get("assets") or []
    for asset in assets:
        if asset.get("asset_type") == "image" and asset.get("file_path"):
            return _join_public_url(asset.get("file_path"))
    return _join_public_url(project.get("thumbnail_path"))


def render_projects_grid(projects: List[Dict[str, Any]]) -> str:
    """Render project cards grid."""
    if not projects:
        return "<div class='status-msg'>No public projects match this filter yet.</div>"

    cards: List[str] = []
    for project in projects:
        title = _escape(project.get("title") or "Untitled")
        project_type = _escape(project.get("project_type") or "general")
        summary = _escape(project.get("short_description") or "No summary available yet.")
        cover_url = _pick_cover(project)
        cover_img = (
            f"<img class='project-cover' src='{_escape(cover_url)}' alt='{title} cover'/>"
            if cover_url
            else "<div class='project-cover'></div>"
        )

        tech_html = "".join(
            f"<span class='tech-chip'>{_escape(tech.get('name'))}</span>"
            for tech in (project.get("technologies") or [])
        )

        links = []
        if project.get("live_url"):
            links.append(
                f"<a class='project-link live' href='{_escape(project.get('live_url'))}' target='_blank' rel='noopener'>Live</a>"
            )
        if project.get("github_url"):
            links.append(
                f"<a class='project-link code' href='{_escape(project.get('github_url'))}' target='_blank' rel='noopener'>Code</a>"
            )

        cards.append(
            f"""
            <article class='project-card'>
              {cover_img}
              <div class='project-body'>
                <h3 class='project-title'>{title}</h3>
                <div class='project-type'>{project_type}</div>
                <p class='project-desc'>{summary}</p>
                <div class='tech-row'>{tech_html}</div>
                <div style='margin-top: 10px;'>{''.join(links)}</div>
              </div>
            </article>
            """
        )

    return f"<section class='projects-grid'>{''.join(cards)}</section>"


def render_project_detail(project: Optional[Dict[str, Any]]) -> str:
    """Render single project detail panel."""
    if not project:
        return "<div class='status-msg'>Select a project to view the full case study.</div>"

    title = _escape(project.get("title") or "Untitled")
    project_type = _escape(project.get("project_type") or "general")
    description = _escape(project.get("full_description") or project.get("short_description") or "No details provided.")

    tech_html = "".join(
        f"<span class='tech-chip'>{_escape(tech.get('name'))}</span>"
        for tech in (project.get("technologies") or [])
    )

    links = []
    if project.get("live_url"):
        links.append(
            f"<a class='project-link live' href='{_escape(project.get('live_url'))}' target='_blank' rel='noopener'>Open live build</a>"
        )
    if project.get("github_url"):
        links.append(
            f"<a class='project-link code' href='{_escape(project.get('github_url'))}' target='_blank' rel='noopener'>View source</a>"
        )

    asset_images = []
    for asset in sorted(project.get("assets") or [], key=lambda item: item.get("sort_order", 0)):
        if asset.get("asset_type") != "image":
            continue
        image_url = _join_public_url(asset.get("file_path"))
        if image_url:
            asset_images.append(
                f"<img src='{_escape(image_url)}' alt='{title} asset' loading='lazy'/>"
            )

    gallery_html = (
        f"<div class='assets-grid'>{''.join(asset_images)}</div>"
        if asset_images
        else "<div class='meta-line'>No gallery assets attached to this project yet.</div>"
    )

    return f"""
        <section class='portfolio-panel'>
      <h3 class='section-title'>{title}</h3>
      <div class='project-type'>{project_type}</div>
      <p>{description}</p>
      <div class='tech-row'>{tech_html}</div>
      <div style='margin-top: 10px;'>{''.join(links)}</div>
      {gallery_html}
    </section>
    """


async def load_profile_section() -> tuple[str, str]:
    """Load and render profile + CV panels."""
    profile = await api_get_public("/portfolio/profile")
    if not profile:
        error = "<div class='status-msg error'>Unable to load profile right now.</div>"
        return error, error
    return render_profile_card(profile), render_cv_panel(profile)


def _normalize_filter(value: Optional[str]) -> Optional[str]:
    if not value or value == "All":
        return None
    return value


def _collect_project_types(projects: List[Dict[str, Any]]) -> List[str]:
    values = {project.get("project_type") for project in projects if project.get("project_type")}
    return sorted(values)


def _project_choices(projects: List[Dict[str, Any]]) -> List[tuple[str, str]]:
    return [(project.get("title", "Untitled"), project.get("slug", "")) for project in projects if project.get("slug")]


async def fetch_projects(technology: Optional[str] = None, project_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch filtered public projects."""
    params: Dict[str, str] = {}
    if technology:
        params["technology"] = technology
    if project_type:
        params["project_type"] = project_type

    projects = await api_get_public("/portfolio/projects", params=params or None)
    if isinstance(projects, list):
        return projects
    return []


async def init_projects_tab():
    """Initialize project filters and first detail view."""
    technologies = await api_get_public("/portfolio/technologies") or []
    projects = await fetch_projects()

    tech_choices = ["All"] + sorted(
        [item.get("name") for item in technologies if isinstance(item, dict) and item.get("name")]
    )
    type_choices = ["All"] + _collect_project_types(projects)

    choices = _project_choices(projects)
    first_slug = choices[0][1] if choices else None
    detail = render_project_detail(projects[0] if projects else None)

    return (
        projects,
        gr.update(choices=tech_choices, value="All"),
        gr.update(choices=type_choices, value="All"),
        render_projects_grid(projects),
        gr.update(choices=choices, value=first_slug),
        detail,
    )


async def apply_project_filters(technology: str, project_type: str):
    """Apply project filters and refresh both cards and detail view."""
    projects = await fetch_projects(_normalize_filter(technology), _normalize_filter(project_type))
    type_choices = ["All"] + _collect_project_types(projects)
    selected_type = project_type if project_type in type_choices else "All"

    choices = _project_choices(projects)
    first_slug = choices[0][1] if choices else None
    detail = render_project_detail(projects[0] if projects else None)

    return (
        projects,
        gr.update(choices=type_choices, value=selected_type),
        render_projects_grid(projects),
        gr.update(choices=choices, value=first_slug),
        detail,
    )


async def show_project_detail(slug: Optional[str], projects: List[Dict[str, Any]]):
    """Render selected project detail, fetching directly if state misses it."""
    if not slug:
        return render_project_detail(None)

    for project in projects or []:
        if project.get("slug") == slug:
            return render_project_detail(project)

    fetched = await api_get_public(f"/portfolio/projects/{slug}")
    if isinstance(fetched, dict):
        return render_project_detail(fetched)

    return "<div class='status-msg error'>Unable to load project details.</div>"


def _error_message(payload: Dict[str, Any]) -> str:
    detail = payload.get("detail")
    if isinstance(detail, list):
        return "; ".join(str(item.get("msg", item)) for item in detail)
    if detail:
        return str(detail)
    return "Request failed. Please review the form and try again."


async def submit_quote(
    name: str,
    email: str,
    company: str,
    phone: str,
    project_type: str,
    budget_range: str,
    timeline: str,
    description: str,
):
    """Submit quote request to public endpoint and return status + optional reset values."""
    name = (name or "").strip()
    email = (email or "").strip()
    description = (description or "").strip()

    if not name or not email or not description:
        return (
            "<div class='status-msg error'>Name, email, and project description are required.</div>",
            name,
            email,
            company,
            phone,
            project_type,
            budget_range,
            timeline,
            description,
        )

    payload = {
        "name": name,
        "email": email,
        "company": company.strip() or None,
        "phone": phone.strip() or None,
        "project_type": project_type.strip() or None,
        "budget_range": budget_range.strip() or None,
        "timeline": timeline.strip() or None,
        "description": description,
    }

    status_code, response = await api_post_public("/contact/quote", payload)
    if status_code == 201:
        quote_id = _escape(str(response.get("id", "")))
        return (
            (
                "<div class='status-msg success'>"
                "Quote request sent successfully. "
                f"Reference: <span class='mono'>{quote_id}</span>"
                "</div>"
            ),
            "",
            "",
            "",
            "",
            "Data Platform",
            "50k-100k MXN",
            "6-8 weeks",
            "",
        )

    return (
        f"<div class='status-msg error'>{_escape(_error_message(response))}</div>",
        name,
        email,
        company,
        phone,
        project_type,
        budget_range,
        timeline,
        description,
    )


def create_app() -> gr.Blocks:
    """Build the portfolio Gradio application."""
    sky_images = _configured_sky_images()

    with gr.Blocks(
        title="Public Portfolio",
        theme=gr.themes.Base(),
        css=CUSTOM_CSS,
                head=THEME_HEAD_HTML,
    ) as app:
        gr.HTML(render_sky_style_vars(sky_images))
        gr.HTML(render_hero_header(sky_images))

        with gr.Tabs(elem_classes=["tab-shell"]):
            with gr.TabItem("Profile"):
                profile_card = gr.HTML("<div class='status-msg'>Loading profile...</div>")
                cv_panel = gr.HTML("<div class='status-msg'>Loading CV...</div>")

            with gr.TabItem("Projects"):
                project_state = gr.State([])

                with gr.Row():
                    technology_filter = gr.Dropdown(label="Technology", choices=["All"], value="All")
                    project_type_filter = gr.Dropdown(label="Project Type", choices=["All"], value="All")
                    apply_filters_btn = gr.Button("Apply Filters", variant="primary")

                projects_grid = gr.HTML("<div class='status-msg'>Loading projects...</div>")
                project_picker = gr.Dropdown(
                    label="Project Detail",
                    choices=[],
                    value=None,
                    interactive=True,
                )
                project_detail = gr.HTML("<div class='status-msg'>Select a project to view details.</div>")

                apply_filters_btn.click(
                    fn=apply_project_filters,
                    inputs=[technology_filter, project_type_filter],
                    outputs=[project_state, project_type_filter, projects_grid, project_picker, project_detail],
                )

                project_picker.change(
                    fn=show_project_detail,
                    inputs=[project_picker, project_state],
                    outputs=[project_detail],
                )

            with gr.TabItem("Contact"):
                gr.HTML(
                    """
                                        <section class='portfolio-panel'>
                      <h2 class='section-title'>Request a Quote</h2>
                      <p class='meta-line'>
                        Share your goals and timeline. You will receive a project response with scope and pricing bands.
                      </p>
                    </section>
                    """
                )

                with gr.Row():
                    name = gr.Textbox(label="Name *", placeholder="Your full name")
                    email = gr.Textbox(label="Email *", placeholder="you@example.com")

                with gr.Row():
                    company = gr.Textbox(label="Company", placeholder="Company name")
                    phone = gr.Textbox(label="Phone", placeholder="+52 ...")

                with gr.Row():
                    project_type = gr.Dropdown(
                        label="Project Type",
                        choices=[
                            "Data Platform",
                            "Machine Learning Model",
                            "Dashboard and Reporting",
                            "LLM Integration",
                            "Data Engineering",
                            "Other",
                        ],
                        value="Data Platform",
                    )
                    budget_range = gr.Dropdown(
                        label="Budget Range",
                        choices=[
                            "Under 50k MXN",
                            "50k-100k MXN",
                            "100k-250k MXN",
                            "250k+ MXN",
                        ],
                        value="50k-100k MXN",
                    )
                    timeline = gr.Dropdown(
                        label="Timeline",
                        choices=["2-4 weeks", "4-6 weeks", "6-8 weeks", "8+ weeks", "Flexible"],
                        value="6-8 weeks",
                    )

                description = gr.Textbox(
                    label="Project Description *",
                    placeholder="Describe your current challenge, expected outcome, and constraints.",
                    lines=8,
                )

                submit_quote_btn = gr.Button("Send Quote Request", variant="primary")
                quote_status = gr.HTML("<div class='status-msg'>Your message has not been sent yet.</div>")

                submit_quote_btn.click(
                    fn=submit_quote,
                    inputs=[name, email, company, phone, project_type, budget_range, timeline, description],
                    outputs=[
                        quote_status,
                        name,
                        email,
                        company,
                        phone,
                        project_type,
                        budget_range,
                        timeline,
                        description,
                    ],
                )

        app.load(load_profile_section, outputs=[profile_card, cv_panel])
        app.load(
            init_projects_tab,
            outputs=[project_state, technology_filter, project_type_filter, projects_grid, project_picker, project_detail],
        )

    return app


if __name__ == "__main__":
    create_app().launch(server_name="0.0.0.0", server_port=7860)
