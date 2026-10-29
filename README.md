# Fruit Atlas — a world encyclopedia of fruits

A multi-page Node.js website for exploring fruit species, named cultivars, regional forms, fruit botany, nutrition, harvest seasons, storage and home growing. The project follows a light, editorial design with a fruit-inspired palette of plum, berry, mango, citrus and leaf tones.

## Catalogue and learning library

The catalogue brings together core species profiles, named cultivar entries and clearly labelled fruit-form guides. It is intended as a broad educational index rather than a claim that every fruit form is independently taxonomically verified or every cultivar entry is a complete breeder record.

The site includes browsing collections and an educational library covering fruit science, chemistry, biology, nutrition, flavour and cooking, ripening and food safety, horticulture, world fruit cultures, ecology and sustainability, and buying and identification skills. Each subject has a collapsible group in the hamburger sidebar; the learning index supports keyword and subject filtering. A dedicated **Fruit chemistry & biology** hub covers sugars and acids, pigments, aroma, texture, flowers and pollination, hormones, seed dispersal and the structure of fruit tissues.

Other features include a glossary, full-text catalogue search, type-ahead suggestions, side-by-side comparison, regional-origin overview, sitemap, robots file, responsive sidebar and expandable multi-column footer.

## UI maintenance update — October 28, 2026

- Repaired an unbalanced parenthesis in the main stylesheet that could stop the browser from applying later page and responsive rules.
- Standardised the content edge and maximum editorial width across interior sections.
- Reworked the sidebar into simple, collapsible navigation groups and made the long sidebar independently scrollable.
- Moved the site footer outside the main landmark and made it settle at the bottom on short pages.
- Improved image fallback handling and added keyboard navigation and ARIA state for search suggestions.
- Expanded the learning library with focused chemistry and biology articles, forest and botanical photography, a science landing page, and subject-linked hamburger navigation.
- Updated the catalogue builder to preserve all additional authored learning guides when regenerating the data files.
- Extended `npm run check` to validate shared layout structure, footer guide links, and CSS delimiter balance.

## Run locally on Windows

**Requirements:** Node.js 20 or newer and npm.

### Option A — easiest

1. Extract this ZIP to a normal folder, for example `D:\about_fruits`.
2. Double-click `START-WEBSITE.bat`.
3. On the first run, the launcher installs the two Node.js dependencies, starts the server and opens `http://localhost:3000`.

### Option B — PowerShell / VS Code terminal

```powershell
cd D:\about_fruits
npm install
npm start
```

Open **http://localhost:3000** in your browser. Keep the terminal open while using the website. Stop the server with `Ctrl+C`.

To use a different port:

```powershell
$env:PORT = "3001"
npm start
```

## Main routes

| Route | Purpose |
| --- | --- |
| `/` | Home and discovery page |
| `/fruits` | Paginated, searchable catalogue with profile-type and group filters |
| `/fruit/:slug` | A full species, cultivar or fruit-form profile |
| `/families` | Browse fruit collections |
| `/family/:slug` | Paginated collection index |
| `/search?q=mango` | Search results with live type-ahead suggestions |
| `/compare?left=apple&right=mango` | Side-by-side profile comparison |
| `/regions` | Broad geographic origin explorer |
| `/benefits` | General fruit nutrition, with cautious non-medical language |
| `/seasonal-calendar` | Interactive overview of harvest context by climate zone |
| `/storage` | Ripeness, storage and handling guide |
| `/growing` | Fruit-growing choices and planning basics |
| `/guides` | Searchable educational learning library with subject filters |
| `/fruit-science` | Fruit chemistry and biology learning hub |
| `/glossary` | Searchable botanical glossary |
| `/sitemap.xml` | XML sitemap covering static and catalogue pages |

## Data files

- `data/fruits.json` — combined catalogue loaded by the app.
- `data/base-fruits.json` — species seed profiles.
- `data/named-cultivars.json` — named cultivar entries.
- `data/fruit-form-profiles.json` — form-guide records included in the final catalogue.
- `data/groups.json` — fruit-group metadata and counts.
- `data/guides.json` — long-form educational articles, grouped by subject and linked in the collapsible sidebar.
- `data/glossary.json` — glossary entries.
- `data/catalogue-stats.json` — profile counts.
- `scripts/build-catalogue.py` — rebuilds the JSON data files from the included seed definitions.

After editing the generator, rebuild from the project directory with:

```powershell
python scripts\build-catalogue.py
npm run check
```

## Images

Profile cards include image fallbacks from public Unsplash image URLs. In the browser, the image loader also attempts to resolve a more specific image from the Wikipedia REST summary API for the fruit name when one is available. The pages and catalogue themselves are served locally; photos need internet access and may fall back to the category image if no matching online image can be found.

The front-end does not display image-credit panels or source UI. For any public deployment, review the external photo endpoints and their usage terms and consider storing a curated, appropriately licensed image set in `public/img/`.

## Validation

Run:

```powershell
npm run check
```

The checks verify JavaScript syntax, catalogue integrity, unique slugs, parent links, required profile fields, template syntax, and the core content files. The site uses Express and EJS; dependencies are installed through npm and are not bundled in the ZIP.


## Fruit chemistry and biology
The learning library includes focused articles on fruit sugars and acids, pigments, aroma compounds, pectin and texture, flower-to-fruit development, plant hormones, seeds and dispersal, and fruit cell structure. Guide illustrations use remote photo URLs and require an internet connection to display.


## Editorial learning-page layout

Learning articles use a split editorial hero with the title and introduction on the left and a topic-specific nature / fruit photograph on the right on desktop. On narrow screens, the hero stacks title-first with the image beneath it. Each guide has a distinct primary image URL; the image loader falls back gracefully if a remote photo is unavailable. The styling lives in `public/css/quality-fixes.css`, and photo assignments are maintained in `server.js`.

## Learning-library photography

Every educational guide has a dedicated image entry in `data/guide-images.json`. The photo IDs are unique across the guide collection, and the science hub uses separate primary photos. Guide images are not cycled through a shared category pool and guide pages do not substitute a repeated generic fallback when a remote image fails. Images are served from Unsplash and therefore require an internet connection. The flavour and cooking guides use fruit/food-oriented imagery rather than a set of landscape-only images.

## Mobile and tablet layout

The shared layout now includes a dedicated `public/css/responsive-polish.css` layer. It adapts the navigation, search field, off-canvas hamburger sidebar, editorial article heroes, catalogue grids, fruit profile pages, science pages, filters, comparison tables and multi-column footer for tablets and narrow phone screens. Controls have larger touch targets, text can wrap safely, comparison tables remain horizontally scrollable within their own container, and the layout respects mobile safe-area insets and reduced-motion preferences.
