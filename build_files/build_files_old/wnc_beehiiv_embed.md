<!--
  WNC GOLF INSIDER — DIRECTORY EMBED v3
  Paste into Beehiiv: Course Directory page → Embed block → Code tab
  Data: https://raw.githubusercontent.com/davebedingfield/wnc-golf-data/main/wnc_courses.json
  To update courses: edit wnc_courses.json on GitHub. No code changes needed.
-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --cream: #faf7ea;
    --green: #1f8d2f;
    --black: #030712;
    --white: #ffffff;
    --ink:   #1a1a1a;
    --muted: #6b6b6b;
    --border:#9ca3af;
    --pub:   #1f8d2f;
    --semi:  #7c5a0a;
    --resort:#185fa5;
    --priv:  #7a1f3a;
    --helene:#991f1f;
  }

  body { font-family: "Crimson Text", Georgia, serif; background: var(--white); color: var(--ink); font-size: 20px; line-height: 1.6; -webkit-font-smoothing: antialiased; }

  /* Filter bar */
  .filter-wrap { background: var(--white); padding: 16px 0 0; }
  .filter-bar { display: flex; gap: 12px; align-items: center; width: 100%; }
  .filter-select { font-family: Helvetica, Arial, sans-serif; font-size: 15px; font-weight: 500; padding: 10px 36px 10px 14px; border: 1px solid var(--border); border-radius: 2px; background: var(--white); color: var(--ink); cursor: pointer; flex: 1; appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236b6b6b' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; transition: border-color .15s; }
  .filter-select:focus { outline: none; border-color: var(--green); }
  .filter-select.active { border-color: var(--green); background-color: #f0faf1; }
  .filter-status { display: flex; align-items: center; padding: 10px 0 0; font-family: "Crimson Text", Georgia, serif; font-size: 20px; color: var(--muted); }
  .filter-reset { font-family: "Crimson Text", Georgia, serif; font-size: 20px; color: var(--green); text-decoration: underline; text-underline-offset: 3px; background: none; border: none; cursor: pointer; padding: 0; }

  @media (max-width: 700px) { .filter-bar { flex-direction: column; } .filter-select { width: 100%; flex: none; } .filter-wrap { padding: 14px 0 0; } }

  /* Subregion header */
  .subregion-header { max-width: 1200px; margin: 0 auto; padding: 32px 0 24px; }
  .subregion-eyebrow { font-family: Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--green); line-height: 24px; margin-bottom: 8px; }
  .subregion-title { font-family: "DM Serif Display", serif; font-size: clamp(40px, 5vw, 56px); font-weight: 800; color: var(--black); line-height: 1.0; margin-bottom: 10px; }
  .subregion-counties { font-size: 20px; line-height: 1.5; color: var(--muted); padding-bottom: 8px; }
  .subregion-vibe { font-size: 20px; line-height: 1.6; color: var(--ink); font-style: italic; padding-bottom: 20px; }

  /* Card grid — 2 col */
  .card-grid { max-width: 1200px; margin: 0 auto; padding: 0 0 64px; display: grid; grid-template-columns: repeat(2, 1fr); column-gap: 56px; row-gap: 80px; }

  /* Card */
  .card { background: var(--white); }

  /* Badges */
  .card-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
  .badge { font-family: Helvetica, Arial, sans-serif; font-size: 10px; letter-spacing: .08em; text-transform: uppercase; padding: 3px 9px; border-radius: 1px; font-weight: 700; }
  .badge.public  { background: #e8f5e9; color: var(--pub); }
  .badge.semi    { background: #fef3e2; color: var(--semi); }
  .badge.resort  { background: #e6f1fb; color: var(--resort); }
  .badge.private { background: #fce8ef; color: var(--priv); }
  .badge.helene  { background: #fdeaea; color: var(--helene); }

  /* Course name */
  .card-name { font-family: "DM Serif Display", serif; font-size: 32px; font-weight: 800; color: var(--black); line-height: 1.2; margin-bottom: 6px; }

  /* County · Terrain */
  .card-city { font-size: 20px; color: var(--muted); line-height: 1.4; margin-bottom: 14px; }

  /* Specs */
  .card-specs { display: flex; margin-bottom: 18px; border: 1px solid var(--border); border-radius: 2px; overflow: hidden; }
  .spec-item { flex: 1; padding: 10px 12px; border-right: 1px solid var(--border); }
  .spec-item:last-child { border-right: none; }
  .spec-label { font-family: Helvetica, Arial, sans-serif; font-size: 9px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); display: block; margin-bottom: 3px; }
  .spec-value { font-family: Helvetica, Arial, sans-serif; font-size: 15px; font-weight: 700; color: var(--black); display: block; }

  /* Summary */
  .card-summary { font-size: 20px; line-height: 1.6; color: var(--ink); margin-bottom: 0; }
  .card-summary em { color: var(--helene); font-style: normal; font-weight: 600; }

  /* Insider tip */
  .insider-tip { display: block; margin-top: 28px; font-size: 20px; line-height: 1.6; color: var(--ink); font-style: italic; }
  .insider-tip::before { content: "Insider tip"; display: block; font-family: Helvetica, Arial, sans-serif; font-size: 12px; font-style: normal; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--black); margin-bottom: 4px; }

  /* Card address & links */
  .card-footer { padding-top: 20px; }
  .card-address { font-size: 20px; color: var(--ink); line-height: 1.5; margin-top: 24px; margin-bottom: 2px; }
  .card-links { font-size: 20px; line-height: 1.5; }
  .card-link { color: var(--green); text-decoration: underline; text-underline-offset: 3px; }
  .card-link:hover { opacity: .7; }

  /* Site footer */
  .site-footer { background: var(--cream); border-top: 1px solid var(--border); text-align: center; padding: 48px 0; font-family: Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.7; color: var(--muted); }
  .site-footer strong { color: var(--black); }

  .card[data-hidden="true"] { display: none; }

  @media (max-width: 700px) {
    .card-grid { grid-template-columns: 1fr; padding: 0 0 48px; column-gap: 0; row-gap: 64px; }
    .subregion-header { padding: 32px 0 20px; }
    .card-name { font-size: 28px; }
  }
</style>

<script>
(function() {
  function fixScroll() {
    try {
      var iframe = window.frameElement;
      if (!iframe) return;
      iframe.setAttribute('scrolling', 'no');
    } catch(e) {}
  }
  fixScroll();
  window.addEventListener('load', fixScroll);
  setTimeout(fixScroll, 1000);
  setTimeout(fixScroll, 3000);
})();
</script>

<div id="wnc-dir-root">
  <div class="filter-wrap">
    <div class="filter-bar">
      <select class="filter-select" id="region-select">
        <option value="all">All Subregions</option>
        <option value="asheville-basin">Asheville Basin</option>
        <option value="high-country">High Country</option>
        <option value="hendersonville-plateau">Hendersonville Plateau</option>
        <option value="smoky-corridor">Great Smoky Mountain Corridor</option>
        <option value="highlands-plateau">Highlands Plateau</option>
        <option value="foothills">Foothills</option>
      </select>
      <select class="filter-select" id="access-select">
        <option value="all">All Access Types</option>
        <option value="public">Public</option>
        <option value="semi-private">Semi-Private</option>
        <option value="resort">Resort</option>
        <option value="private">Private</option>
      </select>
      <select class="filter-select" id="sort-select">
        <option value="alpha">Sort: A &rarr; Z</option>
        <option value="access">Sort: Access Type</option>
      </select>
    </div>
    <div class="filter-status" id="filter-status"></div>
  </div>
  <div id="wnc-dir-content">
    <p style="text-align:center;padding:60px 0;font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#6b6b6b;">Loading courses...</p>
  </div>
</div>

<script>
(function() {
  var DATA_URL = 'https://raw.githubusercontent.com/davebedingfield/wnc-golf-data/main/wnc_courses.json';

  var SUBREGIONS = [
    { slug: 'asheville-basin',        num: '1', title: 'Asheville Basin',
      counties: 'Buncombe \xb7 Madison \xb7 McDowell',
      vibe: 'Rolling valley layouts anchored by the region\u2019s urban core. Historic designs, accessible public tracks, and resort courses within easy reach of downtown Asheville.' },
    { slug: 'high-country',           num: '2', title: 'High Country',
      counties: 'Watauga \xb7 Ashe \xb7 Avery \xb7 Alleghany \xb7 Mitchell \xb7 Yancey',
      vibe: 'Extreme elevations, cool summer escapes, and cliffside designs. The northern spine of the Blue Ridge \u2014 where altitude shapes every shot and the views stop you mid-swing.' },
    { slug: 'hendersonville-plateau', num: '3', title: 'Hendersonville Plateau',
      counties: 'Henderson \xb7 Polk \xb7 Rutherford',
      vibe: 'Mountain plateaus meeting the dramatic eastern escarpment. A mix of refined private clubs and accessible public courses along the ridge where the mountains begin their descent toward the Piedmont.' },
    { slug: 'smoky-corridor',         num: '4', title: 'Great Smoky Mountain Corridor',
      counties: 'Haywood \xb7 Swain \xb7 Cherokee \xb7 Clay \xb7 Graham',
      vibe: 'Deep river valleys framed by the massive Great Smoky and Plott Balsam ranges. Lush, green, and dramatic \u2014 the working heart of WNC mountain golf.' },
    { slug: 'highlands-plateau',           num: '5', title: 'Highlands Plateau',
      counties: 'Macon \xb7 Jackson \xb7 Transylvania',
      vibe: 'The highest concentration of ultra-exclusive private mountain communities in the eastern US, sitting at 3,500 to 4,400+ feet. Cashiers, Highlands, Sapphire, and the Transylvania backcountry \u2014 where the air is thin and the greens are fast.' },
    { slug: 'foothills',              num: '6', title: 'Foothills',
      counties: 'Burke \xb7 Caldwell \xb7 Wilkes \xb7 Catawba',
      vibe: 'Where the Blue Ridge softens into rolling farm country. Laid-back public tracks, underrated private clubs, and some of the best golf values in the WNC region.' }
  ];

  var ACCESS_LABELS = { public: 'Public', semi: 'Semi-Private', 'semi-private': 'Semi-Private', resort: 'Resort', private: 'Private' };
  var BADGE_CLASSES = { public: 'public', semi: 'semi', 'semi-private': 'semi', resort: 'resort', private: 'private' };

  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function buildSpecs(c) {
    if (c.yards || c.slope || c.rating || c.par) {
      var items = '';
      if (c.par)    items += '<div class="spec-item"><span class="spec-label">Par</span><span class="spec-value">' + c.par + '</span></div>';
      if (c.yards)  items += '<div class="spec-item"><span class="spec-label">Yards</span><span class="spec-value">' + String(c.yards).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '</span></div>';
      if (c.rating) items += '<div class="spec-item"><span class="spec-label">Rating</span><span class="spec-value">' + c.rating + '</span></div>';
      if (c.slope)  items += '<div class="spec-item"><span class="spec-label">Slope</span><span class="spec-value">' + c.slope + '</span></div>';
      return items;
    }
    var label = c.spec_label || 'Details';
    var val   = c.spec_value || 'Call pro shop';
    return '<div class="spec-item spec-item--full"><span class="spec-label">' + esc(label) + '</span><span class="spec-value">' + esc(val) + '</span></div>';
  }

  function buildLinks(c) {
    var parts = [];
    if (c.website && !c.website.startsWith('tel:')) {
      var domain = c.website.replace(/https?:\/\//, '').replace(/\/.*/, '').replace(/^www\./, '');
      parts.push('<a class="card-link" href="' + esc(c.website) + '" target="_blank">' + esc(domain) + '</a>');
    }
    if (c.phone) {
      var num = c.phone.replace('tel:', '').replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
      parts.push('<a class="card-link" href="' + esc(c.phone) + '">' + esc(num) + '</a>');
    }
    return parts.join(' &nbsp;\xb7&nbsp; ');
  }

  function buildCard(c) {
    var badgeCls    = BADGE_CLASSES[c.access] || 'public';
    var accessLabel = ACCESS_LABELS[c.access]  || esc(c.access || '');
    var badges = '<span class="badge ' + badgeCls + '">' + accessLabel + '</span>';
    if (c.helene) badges += ' <span class="badge helene">Helene Impact</span>';
    if (c.closed) badges += ' <span class="badge helene">Temporarily Closed</span>';

    var terrain    = esc((c.terrain || '').replace(/-/g, ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); }));
    var county     = esc((c.county || '') + ' County');
    var countyLine = county + (terrain ? ' &nbsp;\xb7&nbsp; ' + terrain : '');
    var addr       = c.address || [c.city, c.county ? c.county + ' County' : '', 'NC'].filter(Boolean).join(', ');
    
    return [
      '<div class="card" data-access="' + badgeCls + '" data-region="' + esc(c.subregion || '') + '">',
      '  <div class="card-body">',
      '    <div class="card-badges">' + badges + '</div>',
      '    <div class="card-name">' + esc(c.name) + '</div>',
      '    <div class="card-city">' + countyLine + '</div>',
      '    <div class="card-specs">' + buildSpecs(c) + '</div>',
      '    <div class="card-summary">' + esc(c.summary || '') + (c.insider_tip ? '<span class="insider-tip">' + esc(c.insider_tip) + '</span>' : '') + '</div>',
      '  </div>',
      '  <div class="card-address">' + esc(addr) + '</div>',
      '  <div class="card-links">' + buildLinks(c) + '</div>',
      '</div>'
    ].join('\n');
  }

  var ACCESS_ORDER = { public: 0, semi: 1, 'semi-private': 1, resort: 2, private: 3 };

  function sortedName(c) {
    return c.name.toLowerCase().replace(/^(the |a |an )/, '');
  }

  function render(data) {
    window._allCourses = data.courses || [];
    initFilters();
  }

  function renderContent(courses, rf, af) {
    var contentEl = document.getElementById('wnc-dir-content');
    var sortSel   = document.getElementById('sort-select');
    var sortMode  = sortSel ? sortSel.value : 'alpha';

    var html = SUBREGIONS.map(function(region) {
      var regionCourses = courses.filter(function(c) { return c.subregion === region.slug; });
      if (!regionCourses.length) return '';
    
      regionCourses = regionCourses.slice().sort(function(a, b) {
        if (sortMode === 'access') {
          var ta = ACCESS_ORDER[a.access] !== undefined ? ACCESS_ORDER[a.access] : 9;
          var tb = ACCESS_ORDER[b.access] !== undefined ? ACCESS_ORDER[b.access] : 9;
          if (ta !== tb) return ta - tb;
        }
        return sortedName(a) < sortedName(b) ? -1 : sortedName(a) > sortedName(b) ? 1 : 0;
      });
    
      return [
        '<div class="subregion-header" data-region-block="' + region.slug + '">',
        '  <div class="subregion-eyebrow">' + (rf === 'all' ? 'Subregion ' + region.num + ' of 6' : 'Subregion') + '</div>',
        '  <h2 class="subregion-title">' + region.title + '</h2>',
        '  <div class="subregion-counties">' + region.counties + '</div>',
        '  <div class="subregion-vibe">' + esc(region.vibe) + '</div>',
        '</div>',
        '<div class="card-grid" data-region-block="' + region.slug + '">',
        regionCourses.map(buildCard).join('\n'),
        '</div>'
      ].join('\n');
    }).join('\n');
    
    html += '<footer class="site-footer"><strong>WNC Golf Insider</strong> \u2014 Complete Regional Course Directory<br>All 6 Subregions \xb7 24 Counties \xb7 83 Courses \xb7 Updated June 2026<br><br>Always call ahead \u2014 course conditions, access policies, and websites change seasonally.</footer>';
    contentEl.innerHTML = html;
    
    if (rf !== 'all') {
      document.querySelectorAll('[data-region-block]').forEach(function(el) {
        el.style.display = el.dataset.regionBlock === rf ? '' : 'none';
      });
    }
  }

  function initFilters() {
    var rSel     = document.getElementById('region-select');
    var aSel     = document.getElementById('access-select');
    var sortSel  = document.getElementById('sort-select');
    var statusEl = document.getElementById('filter-status');

    function applyFilters() {
      var rf       = rSel.value;
      var af       = aSel.value;
      var sortMode = sortSel.value;
    
      rSel.className    = 'filter-select' + (rf !== 'all' ? ' active' : '');
      aSel.className    = 'filter-select' + (af !== 'all' ? ' active' : '');
      sortSel.className = 'filter-select' + (sortMode !== 'alpha' ? ' active' : '');
    
      var filtered = (window._allCourses || []).filter(function(c) {
        var matchRegion = rf === 'all' || c.subregion === rf;
        var matchAccess = af === 'all' || c.access === af;
        return matchRegion && matchAccess;
      });
    
      renderContent(filtered, rf, af);
    
      var visible  = filtered.length;
      var anyFilter = rf !== 'all' || af !== 'all';
      var resetBtn  = anyFilter
        ? ' <span style="color:var(--muted);margin:0 3px">&middot;</span> <button class="filter-reset" id="filter-reset-btn">Reset</button>'
        : '';
      statusEl.innerHTML = '<span>Showing ' + visible + ' golf courses</span>' + resetBtn;
      if (anyFilter) {
        document.getElementById('filter-reset-btn').addEventListener('click', function() {
          rSel.value = 'all'; aSel.value = 'all'; sortSel.value = 'alpha'; applyFilters();
        });
      }
    }
    
    rSel.addEventListener('change', applyFilters);
    aSel.addEventListener('change', applyFilters);
    sortSel.addEventListener('change', applyFilters);
    applyFilters();
  }

  fetch(DATA_URL)
    .then(function(r) { return r.json(); })
    .then(render)
    .catch(function() {
      document.getElementById('wnc-dir-content').innerHTML =
        '<p style="text-align:center;padding:60px 0;font-family:Helvetica,sans-serif;color:#991f1f;">Unable to load course data. Please refresh the page.</p>';
    });
})();
</script>
