'use strict';
const path = require('node:path');
const fs = require('node:fs');
const express = require('express');

const app = express();
const ROOT = __dirname;
const PORT = Number(process.env.PORT) || 3000;
const readJSON = name => JSON.parse(fs.readFileSync(path.join(ROOT, 'data', name), 'utf8'));
const fruits = readJSON('fruits.json');
const species = readJSON('base-fruits.json');
const cultivars = readJSON('named-cultivars.json');
const groups = readJSON('groups.json');
const guides = readJSON('guides.json');
const glossary = readJSON('glossary.json');
const stats = readJSON('catalogue-stats.json');
const bySlug = new Map(fruits.map(item => [item.slug, item]));
const groupBySlug = new Map(groups.map(item => [item.slug, item]));
const guideBySlug = new Map(guides.map(item => [item.slug, item]));
const glossaryBySlug = new Map(glossary.map(item => [item.slug, item]));
const natural = (a, b) => String(a).localeCompare(String(b), 'en', { sensitivity: 'base', numeric: true });
const short = (value, max = 165) => {
  const s = String(value || '').replace(/\s+/g, ' ').trim();
  return s.length > max ? `${s.slice(0, max).replace(/\s+\S*$/, '')}…` : s;
};
const titleCase = s => String(s || '').replace(/\b\w/g, ch => ch.toUpperCase());
const urlForGroup = group => {
  const match = groups.find(item => item.name === group);
  return match ? `/family/${match.slug}` : '/families';
};
const learningCategoryOrder = [
  'Fruit science',
  'Fruit chemistry',
  'Fruit biology',
  'Nutrition & wellbeing',
  'Flavour & cooking',
  'Ripening, storage & safety',
  'Growing & horticulture',
  'World fruits & culture',
  'Ecology & sustainability',
  'Buying, identification & field skills'
];
// Every learning guide has an explicit, unique editorial image assignment in data/guide-images.json.
// Images are not cycled by category and no generic image fallback is applied to guide pages.
const guideImageManifest = readJSON('guide-images.json');
const visualGuides = guides.map(guide => {
  const photo = guideImageManifest[guide.slug];
  if (!photo) throw new Error(`Missing dedicated guide image for ${guide.slug}`);
  return {
    ...guide,
    image: photo.url,
    imageAlt: photo.alt,
    imageCaption: photo.caption
  };
});
const visualGuideBySlug = new Map(visualGuides.map(item => [item.slug, item]));
const navGroups = [
  { title: 'Discover', items: [
    ['Home', '/', 'home'], ['Browse all fruits', '/fruits', 'directory'], ['Search the atlas', '/search', 'search'], ['Compare fruits', '/compare', 'compare'], ['Fruit families', '/families', 'families'], ['Origins around the world', '/regions', 'regions']
  ]},
  { title: 'Food & freshness', items: [
    ['Benefits & nutrition', '/benefits', 'benefits'], ['Harvest seasons', '/seasonal-calendar', 'seasons'], ['Storage & handling', '/storage', 'storage']
  ]},
  { title: 'Growing & care', items: [
    ['Growing fruit at home', '/growing', 'growing'], ['Fruit-growing basics', '/guide/growing-fruit-at-home', 'home-growing']
  ]},
  ...learningCategoryOrder.filter(category => !['Fruit chemistry', 'Fruit biology'].includes(category)).map(category => ({
    title: category,
    items: guides.filter(guide => guide.category === category).map(guide => [guide.title, `/guide/${guide.slug}`, guide.slug])
  })),
  { title: 'Fruit chemistry & biology', items: [
    ['Science overview', '/fruit-science', 'fruit-science'],
    ...guides.filter(guide => ['Fruit chemistry', 'Fruit biology'].includes(guide.category)).map(guide => [guide.title, `/guide/${guide.slug}`, guide.slug])
  ] },
  { title: 'Reference desk', items: [
    ['Learning library', '/guides', 'guides'], ['Glossary', '/glossary', 'glossary'], ['About this atlas', '/about', 'about']
  ]}
];

app.disable('x-powered-by');
app.set('view engine', 'ejs');
app.set('views', path.join(ROOT, 'views'));
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(ROOT, 'public'), { maxAge: '1h', etag: true }));
app.use('/data', express.static(path.join(ROOT, 'data'), { maxAge: '1h', etag: true, fallthrough: false }));

app.locals.siteName = 'Fruit Atlas';
app.locals.short = short;
app.locals.titleCase = titleCase;
app.locals.urlForGroup = urlForGroup;
app.locals.fruitCount = fruits.length;
app.locals.speciesCount = stats.speciesProfiles;
app.locals.cultivarCount = stats.namedCultivars;
app.locals.formCount = stats.fruitFormGuides;
app.locals.guideCount = guides.length;
app.locals.groupCount = groups.length;
app.locals.navGroups = navGroups;
app.locals.groups = groups;
app.locals.guides = visualGuides;
app.locals.glossary = glossary;
app.locals.publicSiteUrl = process.env.PUBLIC_SITE_URL || '';

app.use((req, res, next) => {
  res.locals.currentPath = req.path.replace(/\/$/, '') || '/';
  res.locals.currentQuery = req.query || {};
  res.locals.siteName = 'Fruit Atlas';
  res.locals.navGroups = navGroups;
  res.locals.groups = groups;
  res.locals.publicSiteUrl = String(process.env.PUBLIC_SITE_URL || `${req.protocol}://${req.get('host')}`).replace(/\/+$/, '');
  next();
});

function sortByName(items) { return [...items].sort((a, b) => natural(a.name, b.name)); }
function findFruits(query = {}) {
  let items = fruits;
  const q = String(query.q || '').trim().toLocaleLowerCase();
  const group = String(query.group || '').trim();
  const type = String(query.type || '').trim();
  if (q) items = items.filter(item => (item.searchText || '').includes(q));
  if (group) items = items.filter(item => item.group === group || item.family === group);
  if (type) items = items.filter(item => item.recordType === type);
  return sortByName(items);
}
function paginate(items, page, pageSize = 24) {
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const currentPage = Math.min(Math.max(parseInt(page, 10) || 1, 1), totalPages);
  return { items: items.slice((currentPage - 1) * pageSize, currentPage * pageSize), page: currentPage, pageSize, total: items.length, totalPages,
    start: items.length ? ((currentPage - 1) * pageSize) + 1 : 0, end: Math.min(currentPage * pageSize, items.length) };
}
function relatedTo(fruit, limit = 4) {
  const chosen = (fruit.related || []).map(slug => bySlug.get(slug)).filter(Boolean);
  if (chosen.length >= limit) return chosen.slice(0, limit);
  const fallback = fruits.filter(item => item.slug !== fruit.slug && item.group === fruit.group && !chosen.some(c => c.slug === item.slug));
  return [...chosen, ...fallback].slice(0, limit);
}
function metadata(title, description) { return { pageTitle: title, metaDescription: short(description, 250) }; }

app.get('/', (req, res) => {
  const featuredNames = ['Mango','Apple','Sweet orange','Blueberry','Dragon fruit','Pomegranate','Avocado','Lychee','Grape','Fig','Guava','Watermelon'];
  const featured = featuredNames.map(name => fruits.find(item => item.name.toLowerCase() === name.toLowerCase() && item.recordType === 'Species profile')).filter(Boolean);
  const homeGroups = [...groups].sort((a,b) => b.speciesCount - a.speciesCount).slice(0, 8);
  const featuredGuideSlugs = ['fruit-botany-from-flower-to-fruit', 'fruit-chemistry-sugars-acids-and-balance', 'how-fruit-flowers-become-fruit', 'climate-change-and-shifting-fruit-seasons'];
  const recentGuides = featuredGuideSlugs.map(slug => visualGuideBySlug.get(slug)).filter(Boolean);
  res.render('home', { ...metadata('Fruit Atlas — a world encyclopedia of fruits', 'Explore fruit species, named cultivars, regional forms, growing notes, nutrition, harvest seasons and storage.'), featured, homeGroups, recentGuides });
});

app.get('/fruits', (req, res) => {
  const items = findFruits(req.query);
  const paged = paginate(items, req.query.page, 24);
  res.render('fruit-index', { ...metadata('Explore the fruit catalogue', 'Search and filter thousands of fruit species, named cultivars and editorial form profiles.'), ...paged, q: String(req.query.q || ''), selectedGroup: String(req.query.group || ''), selectedType: String(req.query.type || ''), types: ['Species profile','Named cultivar','Fruit-form guide'] });
});

app.get('/fruit/:slug', (req, res) => {
  const fruit = bySlug.get(req.params.slug);
  if (!fruit) return res.status(404).render('404', metadata('Fruit profile not found', 'The requested profile is not in the Fruit Atlas catalogue.'));
  const related = relatedTo(fruit, 4);
  const parent = fruit.parentSlug ? bySlug.get(fruit.parentSlug) : null;
  const detailTitle = `${fruit.name} — fruit profile | Fruit Atlas`;
  res.render('fruit-detail', { ...metadata(detailTitle, fruit.summary), fruit, related, parent, groupLink: urlForGroup(fruit.group) });
});

app.get('/families', (req, res) => res.render('families', { ...metadata('Fruit families & groups', 'Browse fruit diversity by botanical family, culinary group and growing region.'), groups }));
app.get('/family/:slug', (req, res) => {
  const group = groupBySlug.get(req.params.slug);
  if (!group) return res.status(404).render('404', metadata('Fruit family not found', 'The requested fruit family page is unavailable.'));
  const all = fruits.filter(item => item.group === group.name);
  const paged = paginate(sortByName(all), req.query.page, 24);
  res.render('family-detail', { ...metadata(`${group.name} | Fruit Atlas`, `Explore ${group.name.toLowerCase()}, including species, named cultivars and fruit-form profiles.`), group, ...paged });
});

app.get('/search', (req, res) => {
  const q = String(req.query.q || '').trim();
  const paged = paginate(findFruits({ q, group: req.query.group, type: req.query.type }), req.query.page, 24);
  res.render('search', { ...metadata(q ? `Search results for ${q}` : 'Search the Fruit Atlas', 'Search fruit names, scientific names, plant families, origins and catalogue categories.'), ...paged, q, selectedGroup: String(req.query.group || ''), selectedType: String(req.query.type || '') });
});

app.get('/regions', (req, res) => {
  const map = new Map();
  for (const item of species) {
    const region = item.origin || 'Regional origin varies';
    if (!map.has(region)) map.set(region, []);
    map.get(region).push(item);
  }
  const regionRows = [...map.entries()].map(([name, items]) => ({ name, count: items.length, examples: items.slice(0, 4), image: items[0]?.image })).sort((a,b) => b.count - a.count || natural(a.name,b.name));
  res.render('regions', { ...metadata('Fruit origins around the world', 'Explore the broad geographic origins and growing traditions of fruit species.'), regionRows });
});

app.get('/benefits', (req, res) => res.render('benefits', metadata('Fruit benefits & nutrition', 'A practical, evidence-minded overview of fibre, water, vitamins, plant pigments and how to interpret fruit nutrition.')));
app.get('/seasonal-calendar', (req, res) => res.render('seasons', { ...metadata('Seasonal fruit calendar', 'Explore fruit seasonality across tropical climates and temperate northern and southern hemispheres.'), examples: ['Mango','Mandarin','Apple','Strawberry','Lychee','Watermelon','Grape','Pomegranate'].map(n => species.find(f => f.name.toLowerCase()===n.toLowerCase())).filter(Boolean) }));
app.get('/storage', (req, res) => res.render('storage', metadata('Fruit storage & handling', 'Learn the basics of ripening, refrigeration, cut-fruit handling and reducing waste.')));
app.get('/growing', (req, res) => res.render('growing', metadata('Growing fruit at home', 'Choose fruit plants by climate, sunlight, soil drainage, pollination, mature size and harvest needs.')));
app.get('/about', (req, res) => res.render('about', { ...metadata('About Fruit Atlas', 'How the Fruit Atlas catalogue is structured, what its profile types mean and how to use its educational information.'), stats }));
app.get('/guides', (req, res) => {
  const q = String(req.query.q || '').trim();
  const selectedCategory = String(req.query.category || '').trim();
  const lowerQ = q.toLocaleLowerCase();
  const visibleGuides = visualGuides.filter(guide => {
    const matchesCategory = !selectedCategory || guide.category === selectedCategory;
    const searchable = `${guide.title} ${guide.category} ${guide.intro} ${guide.sections.map(section => `${section.heading} ${section.body}`).join(' ')}`.toLocaleLowerCase();
    return matchesCategory && (!lowerQ || searchable.includes(lowerQ));
  });
  const guideCategories = learningCategoryOrder.map(category => ({ category }));
  res.render('guides', {
    ...metadata('Learning library | Fruit Atlas', 'Explore educational guides to fruit science, nutrition, flavour, ripening, storage, growing, world fruit cultures, ecology, chemistry and biology.'),
    visibleGuides, guideCategories, guideCount: visualGuides.length, q, selectedCategory
  });
});
app.get('/guide/:slug', (req, res) => {
  const guide = visualGuideBySlug.get(req.params.slug);
  if (!guide) return res.status(404).render('404', metadata('Learning guide not found', 'The requested learning guide is unavailable.'));
  const sameCategory = visualGuides.filter(g => g.slug !== guide.slug && g.category === guide.category);
  const otherGuides = visualGuides.filter(g => g.slug !== guide.slug && g.category !== guide.category);
  const relatedGuides = [...sameCategory, ...otherGuides].slice(0, 3);
  res.render('guide-detail', { ...metadata(`${guide.title} | Fruit Atlas`, guide.intro), guide, relatedGuides });
});
app.get('/fruit-science', (req, res) => {
  const chemistryGuides = visualGuides.filter(guide => guide.category === 'Fruit chemistry');
  const biologyGuides = visualGuides.filter(guide => guide.category === 'Fruit biology');
  res.render('science', {
    ...metadata('Fruit chemistry & biology | Fruit Atlas', 'Explore the chemistry of taste, pigments, aroma and texture alongside fruit development, pollination, seeds and plant biology.'),
    chemistryGuides, biologyGuides
  });
});
app.get('/glossary', (req, res) => {
  const q = String(req.query.q || '').trim().toLowerCase();
  const terms = glossary.filter(item => !q || `${item.term} ${item.definition}`.toLowerCase().includes(q));
  res.render('glossary', { ...metadata('Fruit glossary', 'Definitions for fruit botany, ripening, cultivars, growing and food handling.'), terms, q: String(req.query.q || '') });
});
app.get('/glossary/:slug', (req, res) => {
  const term = glossaryBySlug.get(req.params.slug);
  if (!term) return res.status(404).render('404', metadata('Glossary term not found', 'The requested glossary entry is unavailable.'));
  res.render('glossary-detail', { ...metadata(`${term.term} | Fruit Atlas glossary`, term.definition), term });
});
app.get('/compare', (req, res) => {
  const left = bySlug.get(String(req.query.left || 'apple')) || fruits.find(f => f.name === 'Apple' && f.recordType === 'Species profile');
  const right = bySlug.get(String(req.query.right || 'mango')) || fruits.find(f => f.name === 'Mango' && f.recordType === 'Species profile');
  res.render('compare', { ...metadata('Compare fruits', 'Compare fruit species and profiles side by side by flavour, texture, origin, season and common use.'), left, right, selectOptions: sortByName(species).map(f => ({ slug: f.slug, name: f.name, scientificName: f.scientificName })) });
});

app.get('/api/fruits', (req, res) => {
  const query = String(req.query.q || '').trim().toLowerCase();
  const limit = Math.min(Math.max(Number(req.query.limit) || 12, 1), 50);
  const results = findFruits({ q: query, group: req.query.group, type: req.query.type }).slice(0, limit).map(item => ({ slug: item.slug, name: item.name, scientificName: item.scientificName, group: item.group, recordType: item.recordType, url: `/fruit/${item.slug}` }));
  res.json({ total: query ? fruits.filter(item => (item.searchText || '').includes(query)).length : fruits.length, results });
});
app.get('/robots.txt', (req, res) => res.type('text/plain').send(`User-agent: *\nAllow: /\nSitemap: ${res.locals.publicSiteUrl}/sitemap.xml\n`));
function xml(value) { return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;'); }
app.get('/sitemap.xml', (req, res) => {
  const routes = ['','fruits','families','regions','benefits','seasonal-calendar','storage','growing','about','guides','glossary','compare','fruit-science'];
  const urls = routes.map(route => `${res.locals.publicSiteUrl}/${route}`.replace(/([^:]\/)\/+/g,'$1'))
    .concat(fruits.map(item => `${res.locals.publicSiteUrl}/fruit/${item.slug}`))
    .concat(groups.map(g => `${res.locals.publicSiteUrl}/family/${g.slug}`))
    .concat(guides.map(g => `${res.locals.publicSiteUrl}/guide/${g.slug}`))
    .concat(glossary.map(g => `${res.locals.publicSiteUrl}/glossary/${g.slug}`));
  res.type('application/xml').send(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.map(url => `<url><loc>${xml(url)}</loc></url>`).join('')}</urlset>`);
});

app.use((req, res) => res.status(404).render('404', metadata('Page not found', 'The page may have moved or may not be part of the Fruit Atlas.')));
app.use((err, req, res, next) => {
  console.error(err);
  if (res.headersSent) return next(err);
  res.status(500).render('500', metadata('Something went wrong', 'The page could not be rendered. Return to the Fruit Atlas home page and try again.'));
});

if (require.main === module) {
  app.listen(PORT, () => console.log(`Fruit Atlas is running at http://localhost:${PORT}`));
}
module.exports = app;
