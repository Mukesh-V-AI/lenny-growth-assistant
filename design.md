# UX/UI Design Guidelines (Impeccable Style)

This document outlines the design philosophy and structural framework for the frontend of the Lenny Growth Assistant, heavily inspired by modern Impeccable style principles.

## 1. Core Philosophy: The Workspace, Not Just a Chat
Most AI interfaces treat the user like they are texting a vending machine. Our design philosophy pivots the UI from a "Chatbot" to an **"Interactive Workspace."**

When the AI generates an artifact (a markdown essay, HTML code, or a UI component), it must not be dumped into a narrow chat bubble. It must be elevated to a primary view. This is achieved via our **Dual-Pane Architecture**:
- **The Conversational Stream (Left Pane - 40% Width):** For strategy, prompting, and rapid Q&A.
- **The Artifact Workbench (Right Pane - 60% Width):** For deep work, previewing Ship30for30 essays, and interacting with generated UI components.

## 2. Visual Aesthetics (Glassmorphism & Depth)
The application utilizes a premium, dark-mode aesthetic to reduce eye strain for engineers and PMs working late into the night.

- **Background:** Deep slate (`#0F172A`) providing a rich, immersive canvas.
- **Surface Panels:** Translucent, blurred glass panels (Glassmorphism) using `rgba(30, 41, 59, 0.7)` with a heavy backdrop blur (`backdrop-blur-xl`).
- **Borders:** Ultra-thin, low-opacity strokes (`#334155`) to separate elements without creating harsh visual breaks.
- **Accents & Gradients:** Vibrant, electric indigo to purple gradients (`from-indigo-500 to-purple-600`) reserved exclusively for primary actions (like the "Send" button or active LLM toggles). This draws the eye immediately to interactive elements.

## 3. Typography & Scannability
Because the application generates 1250-word Ship30for30 essays, typography is paramount.
- **Font Family:** `Inter` for UI elements (clean, geometric, highly legible).
- **Prose Font:** A beautifully stylized serif or high-contrast sans-serif for the Artifact Viewer to mimic publishing platforms (like Substack or Medium).
- **Hierarchy:** Strict enforcement of heavy bolding for hooks, high line-height (`1.7`) for breathing room, and clear bullet-point indentation.

## 4. Micro-Interactions & State
A premium application feels "alive".
- **Hover States:** All buttons and interactive skill badges subtly scale up (`scale-105`) and increase opacity on hover.
- **Streaming Tokens:** As the FastAPI backend streams tokens via SSE, the text smoothly fades into the chat window, preventing jarring layout shifts.
- **Skill Toggles:** The transition between "General Q&A" and the "Ship30for30" skill is animated via a smooth slide/fade toggle to reinforce that the underlying AI agent has swapped contexts.

## 5. Artifact Viewer Specifications
The Artifact Viewer is the crown jewel of the design.
- **Isolated Sandbox:** HTML/CSS artifacts must render inside a secure `iframe` with zero CSS bleed from the parent application.
- **Toolbar:** A floating, translucent toolbar locked to the top-right of the artifact containing quick-actions: "Copy Markdown", "Download Code", and "Fullscreen".
- **Syntax Highlighting:** Raw code views utilize dark-themed syntax highlighting (e.g., Prism or highlight.js) customized to match the slate aesthetic.
