'use strict';
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..');
const read = file => JSON.parse(fs.readFileSync(path.join(root, 'data', file), 'utf8'));
const fruits = read('fruits.json');
const species = read('base-fruits.json');
const cultivars = read('named-cultivars.json');
const forms = read('fruit-form-profiles.json');
const groups = read('groups.json');
const guides = read('guides.json');
const glossary = read('glossary.json');
const stats = read('catalogue-stats.json');
const errors = [];
const assert = (condition, message) => { if (!condition) errors.push(message); };
const slugs = new Set(fruits.map(item => item.slug));
assert(fruits.length === 2800, `Expected 2,800 catalogue entries, found ${fruits.length}`);
assert(slugs.size === fruits.length, 'Fruit catalogue contains duplicate slugs');
assert(species.length === stats.speciesProfiles, 'Species count does not match catalogue stats');
assert(cultivars.length === stats.namedCultivars, 'Cultivar count does not match catalogue stats');
assert(forms.length === stats.fruitFormGuides, 'Form guide count does not match catalogue stats');
assert(fruits.length === species.length + cultivars.length + forms.length, 'Profile-type files do not sum to the full catalogue');
assert(stats.catalogueRecords === fruits.length, 'Catalogue stats do not match the full catalogue');
assert(groups.length >= 8, 'Expected a broad set of fruit groups');
assert(guides.length >= 60, `Expected an expanded educational library, found ${guides.length} guides`);
assert(new Set(guides.map(guide => guide.slug)).size === guides.length, 'Learning library contains duplicate guide slugs');
const expectedGuideCategories = ['Fruit science','Fruit chemistry','Fruit biology','Nutrition & wellbeing','Flavour & cooking','Ripening, storage & safety','Growing & horticulture','World fruits & culture','Ecology & sustainability','Buying, identification & field skills'];
assert(new Set(guides.map(guide => guide.category)).size === expectedGuideCategories.length, 'Learning-library subject areas do not match the documented set');
for (const category of expectedGuideCategories) assert(guides.some(guide => guide.category === category), `Missing learning-library category: ${category}`);
for (const guide of guides) {
  for (const field of ['slug','title','category','readTime','intro']) if (!guide[field]) errors.push(`Guide ${guide.slug || '(unknown)'} is missing ${field}`);
  if (!Array.isArray(guide.sections) || guide.sections.length < 3) errors.push(`Guide ${guide.slug}: expected at least three content sections`);
  for (const section of guide.sections || []) {
    if (!section.heading || !section.body || section.body.trim().length < 80) errors.push(`Guide ${guide.slug}: section is incomplete or too short`);
  }
}
assert(glossary.length >= 15, 'Expected a useful glossary');
for (const item of fruits) {
  for (const field of ['slug','name','scientificName','family','group','recordType','summary','uniqueness','nutrition','uses','storage','growing','wikiTitle','image']) {
    if (!item[field]) errors.push(`${item.slug}: missing ${field}`);
  }
  if (item.parentSlug && !slugs.has(item.parentSlug)) errors.push(`${item.slug}: parent slug not found (${item.parentSlug})`);
  if (!Array.isArray(item.related) || !Array.isArray(item.benefits)) errors.push(`${item.slug}: related/benefits are not arrays`);
}
for (const file of ['server.js','public/js/site.js']) {
  const { spawnSync } = require('node:child_process');
  const result = spawnSync(process.execPath, ['--check', path.join(root,file)], { encoding: 'utf8' });
  if (result.status !== 0) errors.push(`${file} syntax error: ${result.stderr || result.stdout}`);
}
const compileEjsForSyntaxCheck = (source, filename) => {
  // Lightweight EJS-compatible compiler for static syntax checks. It catches
  // malformed JavaScript inside template tags without needing npm dependencies.
  const tokenPattern = /<%([=#-]?)([\s\S]*?)%>/g;
  let cursor = 0;
  let code = "let __out = '';\nwith (locals) {\n";
  let match;
  while ((match = tokenPattern.exec(source)) !== null) {
    const literal = source.slice(cursor, match.index);
    if (literal) code += `__out += ${JSON.stringify(literal)};\n`;
    const marker = match[1];
    const body = match[2];
    if (marker === '=') code += `__out += escapeHtml(${body});\n`;
    else if (marker === '-') code += `__out += (${body});\n`;
    else if (marker !== '#') code += `${body}\n`;
    cursor = tokenPattern.lastIndex;
  }
  const trailing = source.slice(cursor);
  if (trailing) code += `__out += ${JSON.stringify(trailing)};\n`;
  code += '\n}\nreturn __out;';
  try {
    // EJS uses a with-scope for locals; leave this generated check non-strict.
    new Function('locals', 'escapeHtml', 'include', code); // eslint-disable-line no-new-func
  } catch (error) {
    errors.push(`${filename}: EJS template syntax error: ${error.message}`);
  }
};

// Shared layout regressions: keep the footer outside the main landmark and keep
// the simple accordion sidebar plus its responsive layout stylesheet present.
const sharedHeader = fs.readFileSync(path.join(root, 'views', 'partials', 'head.ejs'), 'utf8');
const sharedEnd = fs.readFileSync(path.join(root, 'views', 'partials', 'end.ejs'), 'utf8');
const fixStyles = fs.readFileSync(path.join(root, 'public', 'css', 'quality-fixes.css'), 'utf8');
assert(sharedHeader.includes('class="content-column"'), 'Shared header is missing the flex content column');
assert(sharedHeader.includes('<main class="main-content" id="mainContent">'), 'Shared header is missing the main landmark');
assert(sharedHeader.includes('<details class="sidebar-group"'), 'Sidebar groups are not collapsible details accordions');
assert(sharedHeader.includes('class="side-link sidebar-learning-simple"') && sharedHeader.includes('href="/guides"'), 'Sidebar is missing the simple educational library link');
assert(!sharedHeader.includes('guideCount'), 'Shared sidebar should not display a guide-count badge');
assert(sharedHeader.includes('/css/quality-fixes.css?v=20261028-square-science-photos-v2'), 'Shared UI fixes stylesheet is not linked');
assert(sharedEnd.trimStart().startsWith('</main>'), 'Shared end partial must close main before rendering the footer');
assert(!sharedEnd.includes('Explore the whole atlas'), 'Footer should not contain the expandable directory drawer');
assert(sharedEnd.includes('footer-main') && sharedEnd.includes('footer-bottom'), 'Footer is missing the new multi-column layout');
assert(sharedEnd.indexOf('</main>') < sharedEnd.indexOf('<footer class="site-footer">'), 'Site footer must be outside the main landmark');
assert(fixStyles.includes('margin-top: auto;'), 'Footer is missing the bottom-alignment flex rule');
assert(fixStyles.includes('overflow-y: auto;'), 'Sidebar is missing its independent vertical scroll');
assert(fixStyles.includes('.guide-library-filter'), 'Learning library filters are missing their layout styles');
assert(fixStyles.includes('.ambient-landscape-banner'), 'Scenic educational page banners are missing');
assert(fixStyles.includes('.guide-article-hero-photo'), 'Learning article split-hero photo styling is missing');
assert(fixStyles.includes('@media (max-width: 680px)'), 'Learning article split hero is missing its mobile layout');
const guideDetailTemplate = fs.readFileSync(path.join(root, 'views', 'guide-detail.ejs'), 'utf8');
assert(guideDetailTemplate.includes('class="guide-article-hero"'), 'Learning article must use the split editorial hero');
assert(guideDetailTemplate.includes('class="guide-article-hero-photo"'), 'Learning article hero must include its right-side photograph');
assert(!guideDetailTemplate.includes('imageFallback') && !guideDetailTemplate.includes('data-image-fallback'), 'Learning article images must not use a repeated generic fallback');
const serverSource = fs.readFileSync(path.join(root, 'server.js'), 'utf8');
const guideImageManifest = read('guide-images.json');
const guideImageEntries = Object.entries(guideImageManifest);
assert(guideImageEntries.length === guides.length, `Expected one explicit image per learning guide, found ${guideImageEntries.length}`);
assert(guides.every(guide => guideImageManifest[guide.slug]), 'At least one learning guide is missing its explicit image assignment');
const primaryPhotoIds = guideImageEntries.map(([, photo]) => photo.photoId);
assert(primaryPhotoIds.every(Boolean), 'Guide image manifest contains an entry without a photo ID');
assert(new Set(primaryPhotoIds).size === primaryPhotoIds.length, 'Learning guides contain duplicate primary photo IDs');
const scienceTemplate = fs.readFileSync(path.join(root, 'views', 'science.ejs'), 'utf8');
const sciencePhotoIds = [...scienceTemplate.matchAll(/images\.unsplash\.com\/(photo-[a-zA-Z0-9-]+)/g)].map(match => match[1]);
assert(sciencePhotoIds.length === 4, `Expected four unique primary science photographs, found ${sciencePhotoIds.length}`);
assert(new Set(sciencePhotoIds).size === sciencePhotoIds.length, 'Science landing repeats one of its primary photos');
assert(sciencePhotoIds.every(id => !primaryPhotoIds.includes(id)), 'Science landing photos must not repeat photos assigned to learning guides');
const guideLibraryTemplate = fs.readFileSync(path.join(root, 'views', 'guides.ejs'), 'utf8');
const libraryHeroMatch = guideLibraryTemplate.match(/images\.unsplash\.com\/(photo-[a-zA-Z0-9-]+)/);
assert(libraryHeroMatch, 'Learning library hero is missing its primary photograph');
if (libraryHeroMatch) assert(!primaryPhotoIds.includes(libraryHeroMatch[1]) && !sciencePhotoIds.includes(libraryHeroMatch[1]), 'Learning library hero must use a photograph unique from guide and science pages');
for (const [slug, photo] of guideImageEntries) {
  assert(photo.url && photo.url.includes(photo.photoId), `Guide ${slug} image URL does not match its photo ID`);
  assert(photo.alt && photo.caption, `Guide ${slug} image assignment is missing alt text or caption`);
}
assert(fs.readFileSync(path.join(root, 'views', 'guides.ejs'), 'utf8').includes('visibleGuides'), 'Learning library index does not use filtered guide results');
assert(!fs.readFileSync(path.join(root, 'views', 'guides.ejs'), 'utf8').includes('data-image-fallback'), 'Learning library images must stay unique without generic fallbacks');
assert(!fs.readFileSync(path.join(root, 'views', 'science.ejs'), 'utf8').includes('data-image-fallback'), 'Science landing photos must not use generic fallbacks');
assert(fixStyles.includes('aspect-ratio: 1 / 1;') && fixStyles.includes('max-width: 980px'), 'Science landing photo must use a capped square layout');
assert(fs.readFileSync(path.join(root, 'server.js'), 'utf8').includes('learningCategoryOrder.filter'), 'Hamburger navigation does not generate subject groups from the learning library');
assert(fs.readFileSync(path.join(root, 'server.js'), 'utf8').includes("app.get('/fruit-science'"), 'Fruit chemistry and biology hub route is missing');
const dragonProfile = fruits.find(item => item.slug === 'dragon-fruit');
assert(dragonProfile && dragonProfile.wikiTitle === 'Dragon fruit', 'Dragon fruit must resolve the fruit article, not the mythical-dragon article');
assert(dragonProfile && dragonProfile.image.includes('upload.wikimedia.org/wikipedia/commons/c/c5/Dragon_fruit.JPG'), 'Dragon fruit must use the verified real-fruit photograph');
assert(fs.readFileSync(path.join(root, 'views', 'fruit-detail.ejs'), 'utf8').includes("fruit.slug !== 'dragon-fruit'"), 'Dragon fruit profile must not replace its direct image with an article title lookup');
const footerGuideSlugs = [...sharedEnd.matchAll(/href="\/guide\/([^"<]+)"/g)].map(match => match[1]);
const guideSlugs = new Set(guides.map(item => item.slug));
for (const slug of ['fruit-chemistry-sugars-acids-and-balance','pigments-in-fruit-and-the-chemistry-of-colour','volatile-aromas-and-fruit-flavour','pectin-enzymes-and-fruit-texture','how-fruit-flowers-become-fruit','fruit-development-and-plant-hormones','seeds-dispersal-and-fruit-evolution','fruit-cell-structure-and-water']) assert(guideSlugs.has(slug), `Missing chemistry/biology learning article: ${slug}`);
for (const slug of footerGuideSlugs) assert(guideSlugs.has(slug), `Footer links to a missing guide: ${slug}`);

// Check CSS delimiter balance so a missing parenthesis/bracket cannot cause
// browsers to discard the remainder of the shared stylesheet.
const cssDirectory = path.join(root, 'public', 'css');
for (const name of fs.readdirSync(cssDirectory).filter(name => name.endsWith('.css'))) {
  const css = fs.readFileSync(path.join(cssDirectory, name), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
  const stack = [];
  let quote = '';
  let escaped = false;
  const pairs = { ')': '(', ']': '[', '}': '{' };
  for (let index = 0; index < css.length; index++) {
    const char = css[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === '\\') escaped = true;
      else if (char === quote) quote = '';
      continue;
    }
    if (char === '"' || char === "'") { quote = char; continue; }
    if (char === '(' || char === '[' || char === '{') stack.push({ char, index });
    else if (char in pairs) {
      const top = stack.pop();
      if (!top || top.char !== pairs[char]) {
        errors.push(`${name}: unbalanced ${char} at character ${index + 1}`);
        break;
      }
    }
  }
  if (quote) errors.push(`${name}: unterminated string literal`);
  if (stack.length) errors.push(`${name}: unclosed ${stack[stack.length - 1].char} at character ${stack[stack.length - 1].index + 1}`);
}

const templateFiles = [];
const collectTemplates = (folder) => {
  for (const item of fs.readdirSync(folder, { withFileTypes: true })) {
    const full = path.join(folder, item.name);
    if (item.isDirectory()) collectTemplates(full);
    else if (item.name.endsWith('.ejs')) templateFiles.push(full);
  }
};
collectTemplates(path.join(root, 'views'));
for (const fullPath of templateFiles) {
  const file = path.relative(path.join(root, 'views'), fullPath);
  const source = fs.readFileSync(fullPath, 'utf8');
  if (!file.startsWith('partials' + path.sep)) {
    if (!source.includes("include('partials/head')")) errors.push(`${file}: does not include the shared header`);
    if (!source.includes("include('partials/end')")) errors.push(`${file}: does not include the shared footer and closing layout`);
  }
  compileEjsForSyntaxCheck(source, file);
}
if (errors.length) {
  console.error(`Fruit Atlas checks failed (${errors.length} issue(s)):`);
  errors.forEach(error => console.error(` - ${error}`));
  process.exitCode = 1;
} else {
  console.log('Fruit Atlas checks passed.');
  console.log('  Unique catalogue pages, profile links and section content validated');
  console.log(`  ${groups.length} fruit groups · ${guides.length} learning guides in ${new Set(guides.map(guide => guide.category)).size} subject areas · ${glossary.length} glossary terms`);
}
