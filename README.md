# WebSummit - Interactive Event Timeline

An interactive, user-friendly timeline of all official WebSummit events, one page per edition. It gives a clearer view of the conference schedule than the official site: browse, filter and explore talks, masterclasses and meetups across every stage.

**[➡️ Open the live site](https://matteo-trevisan.github.io/WebSummit-2025/)**

| Edition | Link |
| ------- | ---- |
| **2026** | [matteo-trevisan.github.io/WebSummit-2025/2026/](https://matteo-trevisan.github.io/WebSummit-2025/2026/) |
| 2025 | [matteo-trevisan.github.io/WebSummit-2025/2025/](https://matteo-trevisan.github.io/WebSummit-2025/2025/) |

---

## ✨ Features

*   **Interactive Timeline:** Pan and zoom through the whole conference schedule.
*   **Grouped by Location:** Events are organized by stage or venue, with a logical sorting order (e.g. Centre Stage first).
*   **Filter by Track:** Highlight every event of a track ("SaaS Summit", "AI Summit", ...) from the dropdown menu.
*   **Detailed Event Modal:** Click an event to see its description, exact times and speakers.
*   **Speaker & Location Links:** Jump to the official speaker profiles and venue maps on the WebSummit website.
*   **Live Indicator:** A red line marks the current time, so you can see what's happening *now*.
*   **Responsive Design:** Works on desktop and mobile browsers.

## 📁 Repository structure

```
.
├── index.html        # Landing page with links to every edition (GitHub Pages entry point)
├── scraper_v2.py     # Downloads the schedule from the WebSummit API
├── 2025/             # WebSummit 2025 timeline
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   ├── open-link.svg
│   └── websummit_schedule.json
└── 2026/             # WebSummit 2026 timeline (same structure)
```

Each year folder is a self-contained static app: it loads its own `websummit_schedule.json` and renders it.

## 🛠️ Tech Stack

*   **Frontend:** HTML5, JavaScript (ES6+)
*   **Styling:** [Tailwind CSS](https://tailwindcss.com/)
*   **Timeline Visualization:** [vis.js Timeline](https://visjs.github.io/vis-timeline/docs/timeline/)
*   **Date/Time Handling:** [Day.js](https://day.js.org/)
*   **Scraper:** Python 3 + [requests](https://requests.readthedocs.io/)

## 🕷️ Updating the schedule (scraper)

`scraper_v2.py` queries the public WebSummit API (`https://websummit.com/api/list/`): it first reads the conference dates, then downloads every page of events for each day and saves them all into one JSON file.

```bash
pip install requests
python3 scraper_v2.py
```

The script writes `websummit_schedule_completo_v5.json` in the current directory. Rename it to `websummit_schedule.json` and move it into the folder of the current edition:

```bash
mv websummit_schedule_completo_v5.json 2026/websummit_schedule.json
```

> The scraper doesn't take a year: it downloads whatever edition the WebSummit API is serving at the moment (normally the upcoming one). Keep past years' JSON files as they are.

## 🚀 Running locally

No build step is required. Because the pages load the JSON with `fetch`, serve the repository with a local web server instead of opening the files directly:

```bash
# From the repository root
python3 -m http.server
```

Then open `http://localhost:8000` in your browser.

## 📄 License

[GNU AGPL v3](2026/LICENSE)
