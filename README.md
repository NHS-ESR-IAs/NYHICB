# ESR Manager Hub – Humber and North Yorkshire ICB

A small standalone website that supports managers using **ESR Manager Self Service (MSS)**, plus a simple portlet that sends people from ESR to the site.

```
site/                      ← the website (publish this folder)
  index.html               Home: topics, quick links, new starter journey, help
  guide.html               Step-by-step guide (the MSS training slides, rebuilt)
  learning.html            All 41 ESR online learning guides (GENERATED – see below)
  css/styles.css
  js/main.js               Optional extras only; every page works without JS
  assets/img/              Screenshots from the original PowerPoint
portlet/
  esr-signpost-portlet.html   Paste into an ESR Web Content portlet
tools/
  build_learning.py        Rebuilds learning.html from the Resources file
Resources                  List of MSS online learning guides (source of truth)
```

## 1. Publish the site

The site is plain HTML, CSS and JS. There's no build step and no server code, so any static host will work:

- **ICB web server / intranet**: copy the contents of `site/` into a folder.
- **GitHub Pages**: push the repo, then set Pages to publish from the `/site` folder (or move its contents to `/docs`).
- **Azure Static Web Apps / Netlify**: set the publish directory to `site`.

Preview it locally:

```bash
cd site && python3 -m http.server 8000
# then open http://localhost:8000
```

## 2. Add the signpost portlet to ESR

1. Open `portlet/esr-signpost-portlet.html`.
2. Replace every `https://YOUR-SITE-ADDRESS/` with your published address (5 places).
3. In ESR, edit the Web Content item, switch to **Source / Code** view, and paste **Option A**.
4. If ESR still strips the styling, use **Option B**, the plain-text fallback.

The portlet uses only `div`, `p`, `a`, `span` and `strong` with inline styles. These usually get through Liferay's HTML sanitiser, which is what removed the interactive version.

## 3. Update the online learning library

1. Edit `Resources`. Put each category heading on its own line, followed by its guides as `MSS10: How do I …?`.
2. Run `python3 tools/build_learning.py`.
3. Re-publish `site/`.

Every guide links to `https://my.esr.nhs.uk/dashboard/lrst/<CODE>/index.html`.
To change which guides are marked **★ recommended** or **April 2027**, edit `ESSENTIAL` and `COMING_SOON` at the top of the script.

## Before go-live – please check

- [ ] **Support contact**: `site/index.html` has a placeholder email, `esr.support@example.nhs.net` (search for `TODO`).
- [ ] **ESR events calendar link** (home page, Step 4): `https://my.esr.nhs.uk/dashboard/web/esrweb/events` is a best guess. Please check it.
- [ ] **ESR user manual home link**: `https://my.esr.nhs.uk/dashboard/web/usermanual/home`. Please check it.
- [ ] Spot-check a few `lrst/MSSxx` guide links while logged in to ESR.

## Notes

- Accessibility: skip link, NHS-style focus states, alt text on every screenshot, reduced-motion support, and keyboard-operable zoom and filters.
- The earlier Liferay-only attempts are in `archive/` for reference.

