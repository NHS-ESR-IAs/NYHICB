#!/usr/bin/env python3
"""
Build site/learning.html from the plain-text `Resources` file.

How to update the learning library:
  1. Edit the `Resources` file in the project root (one category heading per line,
     followed by lines like "MSS10: How do I enter an employees sickness absence?").
  2. Run:  python3 tools/build_learning.py
  3. Re-publish the `site/` folder.

Each guide links to https://my.esr.nhs.uk/dashboard/lrst/<CODE>/index.html
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "Resources"
OUT = ROOT / "site" / "learning.html"

GUIDE_URL = "https://my.esr.nhs.uk/dashboard/lrst/{code}/index.html"
STARTER_PACK = "https://my.esr.nhs.uk/dashboard/documents/d/esredu/new-starter-pack-manager-self-service-v2-0-09-2026"

# Friendlier names, descriptions and icons for the headings used in Resources.
CATEGORY_META = {
    "Manager": ("Notifications &amp; worklist", "Approve requests, set vacation rules and manage proxy users.", "🔔"),
    "Talent Profile": ("Talent profile &amp; organisation chart", "See who reports to you and view their talent profile.", "🧭"),
    "My Team Personal Information": ("My team: personal information &amp; absence", "Update personal details and record annual leave, sickness and special leave.", "🗓️"),
    "Manage Hires": ("Manage hires", "Bring a new starter into your team.", "🤝"),
    "Reporting": ("Reporting", "Use the standard ESR Business Intelligence dashboard.", "📊"),
    "My Team Assignment Information": ("My team: assignment changes", "Change hours, locations and managers, and process leavers.", "🧩"),
    "My Team Career Information": ("My team: learning, appraisal &amp; compliance", "Enrol staff on training, run appraisals and keep compliance up to date.", "🎓"),
}

# The guides a new manager is most likely to need first.
ESSENTIAL = {"MSS01", "MSS03", "MSS39", "MSS08", "MSS09", "MSS10", "MSS11",
             "MSS27", "MSS28", "MSS29", "MSS31", "MSS34"}

# Local note from the ICB slides: appraisals roll out from April 2027.
COMING_SOON = {"MSS17": "ICB rollout April 2027",
               "MSS18": "ICB rollout April 2027",
               "MSS41": "ICB rollout April 2027"}

MODULE_RE = re.compile(r"^(MSS\d+)\s*:\s*(.+)$")


def tidy_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    # Restore apostrophes missing from the source list ("employees name" -> "employee's name").
    title = re.sub(r"\bemployees\b(?! in\b)", "employee's", title)
    title = title.replace("teams compliance", "team's compliance")
    return title


def parse_resources(text: str):
    categories, current = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("http") or line.lower().startswith("each guide"):
            continue
        m = MODULE_RE.match(line)
        if m:
            if current is None:
                current = {"name": "Other", "modules": []}
                categories.append(current)
            current["modules"].append((m.group(1), tidy_title(m.group(2))))
        else:
            current = {"name": line, "modules": []}
            categories.append(current)
    return [c for c in categories if c["modules"]]


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def render_module(code, title):
    url = GUIDE_URL.format(code=code)
    essential = "true" if code in ESSENTIAL else "false"
    soon = COMING_SOON.get(code)
    classes = "module" + (" is-soon" if soon else "")
    badge = f' <span class="badge-soon">{html.escape(soon)}</span>' if soon else ""
    star = ' <span title="Recommended for new managers" aria-label="Recommended">★</span>' if code in ESSENTIAL else ""
    search_text = html.escape(f"{code} {title}".lower(), quote=True)
    return f"""          <li class="{classes}" data-code="{code}" data-essential="{essential}" data-search="{search_text}">
            <a class="module-link" href="{url}" target="_blank" rel="noopener">
              <span class="code">{code}{star}</span>
              <span class="title">{html.escape(title)}{badge}</span>
              <span class="ext">Opens ESR online learning ↗<span class="visually-hidden"> (opens in a new tab)</span></span>
            </a>
          </li>"""


def render_category(cat):
    label, desc, icon = CATEGORY_META.get(cat["name"], (html.escape(cat["name"]), "", "📘"))
    cid = slugify(cat["name"])
    items = "\n".join(render_module(c, t) for c, t in cat["modules"])
    desc_html = f"\n        <p>{desc}</p>" if desc else ""
    return f"""      <section class="category" id="{cid}" aria-labelledby="{cid}-h">
        <h2 id="{cid}-h"><span aria-hidden="true">{icon}</span> {label} <span class="count">{len(cat['modules'])}</span></h2>{desc_html}
        <ul class="module-list">
{items}
        </ul>
      </section>"""


def main():
    cats = parse_resources(RESOURCES.read_text(encoding="utf-8"))
    total = sum(len(c["modules"]) for c in cats)
    body = "\n\n".join(render_category(c) for c in cats)
    jump = "\n".join(
        f'            <li><a class="chip" href="#{slugify(c["name"])}">{CATEGORY_META.get(c["name"], (c["name"],))[0]}</a></li>'
        for c in cats)

    page = TEMPLATE.format(total=total, categories=body, jump=jump, starter=STARTER_PACK)
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} with {total} guides in {len(cats)} categories")


TEMPLATE = """<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESR online learning library – Manager Self Service Hub – Humber and North Yorkshire ICB</title>
  <meta name="description" content="Every ESR Manager Self Service online learning guide in one searchable list.">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <!-- GENERATED FILE: edit /Resources and run tools/build_learning.py -->
  <a class="skip-link" href="#main">Skip to main content</a>
  <div class="brand-strip"></div>
  <header class="site-header">
    <div class="container">
      <a class="brand" href="index.html">
        <img class="brand-logo" src="assets/img/icb-nhs-banner.png" alt="NHS Humber and North Yorkshire Integrated Care Board – We Care, We Connect, We Innovate">
        <span class="brand-title"><strong>ESR Manager Hub</strong><span>Manager Self Service support</span></span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav id="site-nav" class="site-nav" aria-label="Main">
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="guide.html">Step-by-step guide</a></li>
          <li><a href="learning.html" aria-current="page">Online learning</a></li>
          <li><a href="index.html#help">Get help</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
    <section class="hero page-hero">
      <div class="container">
        <div>
          <span class="eyebrow">ESR online learning</span>
          <h1>Manager Self Service learning library</h1>
          <p class="lead">All {total} short ESR "How do I…?" guides in one place. Search for a task or browse by category to open the guide straight in ESR.</p>
          <div class="hero-actions">
            <a class="btn btn-light" href="{starter}" target="_blank" rel="noopener">MSS new starter pack ↗</a>
            <a class="btn btn-ghost" href="guide.html">Back to the step-by-step guide</a>
          </div>
        </div>
      </div>
    </section>

    <div class="section">
      <div class="container">
        <div class="callout">
          <strong>Before you start</strong>
          These guides open inside the ESR portal, so you may be asked to log in with your Smartcard first.
        </div>

        <div class="toolbar" role="search">
          <div>
            <label for="module-search">Search the guides</label>
            <input id="module-search" class="search-input" type="search" placeholder="e.g. sickness, leaver, hours, MSS10" autocomplete="off">
          </div>
          <div class="results-count" id="results-count">{total} of {total} guides shown</div>
          <div class="filter-chips" role="group" aria-label="Filter guides">
            <button type="button" data-filter="all" aria-pressed="true">All guides ({total})</button>
            <button type="button" data-filter="essential" aria-pressed="false">★ Recommended for new managers</button>
          </div>
        </div>

        <nav aria-label="Jump to category" style="margin-bottom:26px">
          <ul class="chip-list">
{jump}
          </ul>
        </nav>

        <p id="results-status" class="visually-hidden" role="status" aria-live="polite"></p>

        <div id="library">
{categories}
        </div>

        <div class="empty-state">
          <p><strong>No guides match your search.</strong></p>
          <p>Try a simpler word such as "absence", "address" or "appraisal".</p>
        </div>
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <h2>ESR Manager Hub</h2>
          <p>Local support for managers in NHS Humber and North Yorkshire ICB using ESR Manager Self Service.</p>
        </div>
        <div>
          <h2>On this site</h2>
          <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="guide.html">Step-by-step guide</a></li>
            <li><a href="learning.html">Online learning library</a></li>
          </ul>
        </div>
        <div>
          <h2>Go to ESR</h2>
          <ul>
            <li><a href="https://my.esr.nhs.uk/" target="_blank" rel="noopener">ESR portal ↗</a></li>
            <li><a href="https://my.esr.nhs.uk/dashboard/web/usermanual/home" target="_blank" rel="noopener">ESR user manual ↗</a></li>
          </ul>
        </div>
      </div>
      <p class="footer-meta">Based on the NHSBSA ESR Manager Self Service Functional Guide v2.0. ESR screens and features may vary with local configuration.</p>
    </div>
  </footer>

  <a class="back-top" href="#main">↑ Top</a>
  <script src="js/main.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
