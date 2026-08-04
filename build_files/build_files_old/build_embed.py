import re

# Read CSS from the current v2 HTML (built fresh by build_directory.py)
with open('/home/claude/wnc_directory_v2.html') as f:
    src = f.read()

css_match = re.search(r'<style>(.*?)</style>', src, re.DOTALL)
css = css_match.group(1).strip()

embed = r"""<!--
  WNC GOLF INSIDER — DIRECTORY EMBED v4
  Paste into Beehiiv: Course Directory page → Embed block → Code tab
  Data: https://raw.githubusercontent.com/davebedingfield/wnc-golf-data/main/wnc_courses.json
  To update courses: edit wnc_courses.json on GitHub. No code changes needed.
-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
CSS_PLACEHOLDER
/* Filter bar */
.filter-wrap { background: var(--white); padding: 20px 0 0; max-width: 1200px; margin: 0 auto; }
.filter-bar { display: flex; gap: 12px; }
.filter-select {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 15px;
  font-weight: 500;
  padding: 10px 36px 10px 14px;
  border: 1px solid var(--border);
  border-radius: 2px;
  background: var(--white);
  color: var(--ink);
  cursor: pointer;
  flex: 1;
  appearance: none;
  -webkit-appearance: none;
  -webkit-tap-highlight-color: transparent; url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236b6b6b' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  transition: border-color .15s;
}
.filter-select:focus { outline: none; border-color: var(--green); }
.filter-select.active { border-color: var(--green); }
.filter-status {
  display: flex;
  align-items: center;
  padding: 10px 0 0;
  font-family: "Crimson Text", Georgia, serif;
  font-size: 20px;
  color: var(--muted);
}
.filter-reset {
  font-family: "Crimson Text", Georgia, serif;
  font-size: 20px;
  color: var(--green);
  text-decoration: underline;
  text-underline-offset: 3px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}
@media (max-width: 700px) {
  .filter-bar { flex-direction: column; }
  .filter-wrap { padding: 16px 0 0; }
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
        <option value="all">All access types</option>
        <option value="public">Public</option>
        <option value="semi">Semi-Private</option>
        <option value="resort">Resort</option>
        <option value="private">Private</option>
      </select>
      <select class="filter-select" id="sort-select">
        <option value="alpha">Sort alphabetically</option>
        <option value="access">Sort by access type</option>
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

  var ACCESS_LABELS  = { public: 'Public', semi: 'Semi-Private', 'semi-private': 'Semi-Private', resort: 'Resort', private: 'Private' };
  var BADGE_CLASSES  = { public: 'public', semi: 'semi', 'semi-private': 'semi', resort: 'resort', private: 'private' };

  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function buildSpecs(c) {
    if (c.yards || c.slope || c.rating || c.par) {
      var items = '';
      if (c.yards)  items += '<div class="spec-item"><span class="spec-label">Yards</span><span class="spec-value">' + String(c.yards).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '</span></div>';
      if (c.slope)  items += '<div class="spec-item"><span class="spec-label">Slope</span><span class="spec-value">' + c.slope + '</span></div>';
      if (c.rating) items += '<div class="spec-item"><span class="spec-label">Rating</span><span class="spec-value">' + c.rating + '</span></div>';
      if (c.par)    items += '<div class="spec-item"><span class="spec-label">Par</span><span class="spec-value">' + c.par + '</span></div>';
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
    if (c.tee_times && c.tee_times !== c.website) {
      var tt = c.tee_times;
      var label;
      if (tt.startsWith('tel:')) {
        label = tt.replace('tel:', '').replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
      } else if (/golfnow|tee-time|taimoor/i.test(tt)) {
        label = 'Tee Times';
      } else if (/membership|member/i.test(tt) || c.access === 'private') {
        label = 'Membership Inquiry';
      } else if (/stay|lodg/i.test(tt)) {
        label = 'Stay & Play';
      } else {
        label = 'Tee Times';
      }
      parts.push('<a class="card-link" href="' + esc(tt) + '" target="_blank">' + esc(label) + '</a>');
    }
    if (c.phone && c.phone !== c.tee_times) {
      var num = c.phone.replace('tel:', '').replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
      parts.push('<a class="card-link" href="' + esc(c.phone) + '" target="_blank">' + esc(num) + '</a>');
    }
    return parts.join(' &nbsp;\xb7&nbsp; ');
  }

  function buildCard(c) {
    var badgeCls    = BADGE_CLASSES[c.access] || 'public';
    var accessLabel = ACCESS_LABELS[c.access]  || esc(c.access || '');
    var badges = '<span class="badge ' + badgeCls + '">' + accessLabel + '</span>';
    if (c.helene) badges += ' <span class="badge helene">Helene Impact</span>';
    if (c.closed) badges += ' <span class="badge helene">Temporarily Closed</span>';

    var terrain   = esc((c.terrain || '').replace(/-/g, ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); }));
    var county    = esc((c.county || '') + ' County');
    var countyLine = county + (terrain ? ' &nbsp;\xb7&nbsp; ' + terrain : '');

    var addr = c.address || [c.city, c.county ? c.county + ' County' : '', 'NC'].filter(Boolean).join(', ');

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
    var sortSel = document.getElementById('sort-select');
    var sortMode = sortSel ? sortSel.value : 'alpha';

    var html = SUBREGIONS.map(function(region) {
      // Filter to this subregion
      var regionCourses = courses.filter(function(c) {
        return c.subregion === region.slug;
      });
      if (!regionCourses.length) return '';

      // Sort within region
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
        '  <div class="subregion-eyebrow">Subregion</div>',
        '  <h2 class="subregion-title">' + region.title + '</h2>',
        '  <div class="subregion-counties">' + region.counties + '</div>',
        '</div>',
        '<div class="card-grid" data-region-block="' + region.slug + '">',
        regionCourses.map(buildCard).join('\n'),
        '</div>'
      ].join('\n');
    }).join('\n');

    html += '<footer class="site-footer"><strong>WNC Golf Insider</strong> \u2014 Complete Regional Course Directory<br>All 6 Subregions \xb7 24 Counties \xb7 Updated June 2026<br><br>Always call ahead \u2014 course conditions, access policies, and websites change seasonally.</footer>';
    contentEl.innerHTML = html;

    // Hide sections not matching region filter
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
      var rf = rSel.value, af = aSel.value;
      var sortMode = sortSel.value;

      rSel.className    = 'filter-select' + (rf !== 'all' ? ' active' : '');
      aSel.className    = 'filter-select' + (af !== 'all' ? ' active' : '');
      sortSel.className = 'filter-select' + (sortMode !== 'alpha' ? ' active' : '');

      // Filter courses
      var filtered = (window._allCourses || []).filter(function(c) {
        var matchRegion = rf === 'all' || c.subregion === rf;
        var accessKey = (c.access || '').replace('-', '');
        var matchAccess = af === 'all' || c.access === af || accessKey === af;
        return matchRegion && matchAccess;
      });

      renderContent(filtered, rf, af);

      var visible = filtered.length;
      var anyFilter = rf !== 'all' || af !== 'all';
      var resetBtn = anyFilter
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
"""

# Strip the CSS already in the static HTML that would conflict — just use the relevant rules
# Actually we want the FULL CSS from wnc_directory_v2 minus the filter rules (we write those fresh above)
css_no_filter = re.sub(r'/\* Filter bar.*?@media \(max-width: 700px\) \{.*?\}', '', css, flags=re.DOTALL).strip()

# Strip all left/right padding from layout containers
css_no_filter = css_no_filter.replace('padding: 64px 28px 24px', 'padding: 64px 0 24px')
css_no_filter = css_no_filter.replace('padding: 0 28px 64px', 'padding: 0 0 64px')
css_no_filter = css_no_filter.replace('padding: 48px 28px', 'padding: 48px 0')
css_no_filter = css_no_filter.replace('border-bottom: 1px solid var(--border); padding: 16px 0; position: sticky; top: 0; z-index: 100;', 'padding: 16px 0;')
css_no_filter = css_no_filter.replace('border-bottom: 1px solid var(--border); padding: 16px 28px; position: sticky; top: 0; z-index: 100;', 'padding: 16px 0;')
css_no_filter = css_no_filter.replace('padding: 0 18px 48px', 'padding: 0 0 48px')
css_no_filter = css_no_filter.replace('padding: 48px 18px 20px', 'padding: 48px 0 20px')
# Remove border-bottom from subregion-counties (clean look, no divider)
css_no_filter = css_no_filter.replace('border-bottom: 1px solid var(--border); padding-bottom: 20px', 'padding-bottom: 20px')
# Darken border color — affects dropdowns and spec boxes
css_no_filter = css_no_filter.replace('--border:#e5e7eb;', '--border:#9ca3af;')
css_no_filter = css_no_filter.replace('padding: 64px 0 24px', 'padding: 32px 0 24px')
css_no_filter = css_no_filter.replace('padding: 48px 0 20px', 'padding: 32px 0 20px')
# Increase row-gap for more breathing room between cards
css_no_filter = css_no_filter.replace(
    '.card { background: var(--white); display: flex; flex-direction: column; }',
    '.card { background: var(--white); }'
)
css_no_filter = css_no_filter.replace('.card-body { flex: 1; }', '')
css_no_filter = css_no_filter.replace('row-gap: 52px', 'row-gap: 80px')
css_no_filter = css_no_filter.replace('.card-footer { padding-top: 20px; margin-top: auto; }', '.card-footer { padding-top: 20px; }')
css_no_filter = css_no_filter.replace('row-gap: 40px', 'row-gap: 64px')
css_no_filter = css_no_filter.replace(
    '.card-address { font-size: 20px; color: var(--muted); line-height: 1.5; margin-bottom: 2px; }',
    '.card-address { font-size: 20px; color: var(--ink); line-height: 1.5; margin-top: 24px; margin-bottom: 2px; }'
)
css_no_filter = css_no_filter.replace(
    '.insider-tip { display: block; margin-top: 16px;',
    '.insider-tip { display: block; margin-top: 28px;'
)

embed = embed.replace('CSS_PLACEHOLDER', css_no_filter)

with open('/home/claude/wnc_beehiiv_embed.html', 'w') as f:
    f.write(embed)

print(f"Embed built: {len(embed):,} chars")

# Verify no bad variables
for bad in ['isPrivate', 'isSemi', 'isResort']:
    print(f"  '{bad}' present: {bad in embed}")

# Count key markers
print(f"  buildLinks function: {'function buildLinks' in embed}")
print(f"  Membership Inquiry: {'Membership Inquiry' in embed}")
print(f"  data-region-block on card-grid: {'card-grid\" data-region-block' in embed}")
print(f"  Always-visible status: {'Showing ' in embed}")
