import json, re

with open('/home/claude/wnc_courses.json') as f:
    DATA = json.load(f)

COURSES = DATA['courses']
TOTAL = len(COURSES)

BADGE_CLASSES = {"public": "public", "semi-private": "semi", "resort": "resort", "private": "private"}
ACCESS_LABELS = {"public": "Public", "semi-private": "Semi-Private", "resort": "Resort", "private": "Private"}

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

def linkify(s):
    """Mirror of the live JS linkify(): preserve <em> tags, escape rest, autolink bare URLs."""
    s = s or ""
    em_slots = []
    def stash_em(m):
        em_slots.append(m.group(1))
        return f'\x00em{len(em_slots)-1}\x00'
    s = re.sub(r'<em>([\s\S]*?)</em>', stash_em, s)
    s = esc(s)
    def autolink(m):
        match = m.group(0)
        href = match if re.match(r'^https?://', match, re.I) else 'https://' + match
        return f'<a class="prose-link" href="{href}" target="_blank" rel="noopener">{match}</a>'
    s = re.sub(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:/[^\s,;.!?]*[^\s,;.!?)])?)', autolink, s)
    def restore_em(m):
        i = int(m.group(1))
        return f'<em>{esc(em_slots[i])}</em>'
    s = re.sub(r'\x00em(\d+)\x00', restore_em, s)
    return s

def sorted_name(c):
    return re.sub(r'^(the |a |an )', '', c["name"].lower())

def build_specs(c):
    if c.get("yards") or c.get("slope") or c.get("rating") or c.get("par"):
        items = ""
        if c.get("par"):
            items += f'<div class="spec-item"><span class="spec-label">Par</span><span class="spec-value">{c["par"]}</span></div>'
        if c.get("yards"):
            items += f'<div class="spec-item"><span class="spec-label">Yards</span><span class="spec-value">{c["yards"]:,}</span></div>'
        if c.get("rating"):
            items += f'<div class="spec-item"><span class="spec-label">Rating</span><span class="spec-value">{c["rating"]}</span></div>'
        if c.get("slope"):
            items += f'<div class="spec-item"><span class="spec-label">Slope</span><span class="spec-value">{c["slope"]}</span></div>'
        return items
    return '<div class="spec-item spec-item--full"><span class="spec-label">Rating</span><span class="spec-value">Not rated</span></div>'

def build_location(c):
    addr = c.get("address") or ", ".join(filter(None, [c.get("city"), f'{c.get("county")} County' if c.get("county") else "", "NC"]))
    addr_html = ""
    if addr:
        last_comma = addr.rfind(", ")
        second_last = addr.rfind(", ", 0, last_comma) if last_comma > 0 else -1
        split_at = second_last if second_last > -1 else last_comma
        if split_at > -1:
            line1, line2 = addr[:split_at], addr[split_at+2:]
        else:
            line1, line2 = addr, ""
        addr_html = f'<div class="card-location-address">{esc(line1)}{("<br>" + esc(line2)) if line2 else ""}</div>'

    contact_html = ""
    website = c.get("website")
    if website and not website.startswith("tel:"):
        domain = re.sub(r'^https?://', '', website)
        domain = re.sub(r'/.*$', '', domain)
        domain = re.sub(r'^www\.', '', domain)
        contact_html += f'<div class="card-location-contact"><a href="{esc(website)}" target="_blank">{esc(domain)}</a></div>'
    phone = c.get("phone")
    if phone:
        num = phone.replace("tel:", "")
        num = re.sub(r'(\d{3})(\d{3})(\d{4})', r'(\1) \2-\3', num)
        contact_html += f'<div class="card-location-contact"><a href="{esc(phone)}">{esc(num)}</a></div>'

    return addr_html + contact_html

def build_footnote(c):
    if c.get("usga_rating_note"):
        return f'<div class="card-footnote">{esc(c["usga_rating_note"])}</div>'
    return ""

def build_card(c):
    access = c.get("access", "public")
    badge_cls = BADGE_CLASSES.get(access, "public")
    access_label = ACCESS_LABELS.get(access, esc(access))
    badges = f'<span class="badge {badge_cls}">{access_label}</span>'
    if c.get("helene"):
        badges += ' <span class="badge helene">Helene Impact</span>'
    if c.get("closed"):
        badges += ' <span class="badge helene">Temporarily Closed</span>'

    summary = linkify(c.get("summary", ""))
    tip = c.get("insider_tip")
    tip_html = f'<span class="insider-tip">{linkify(tip)}</span>' if tip else ""

    return "\n".join([
        f'<div class="card" data-access="{badge_cls}" data-region="{esc(c.get("subregion",""))}">',
        f'  <div class="card-body">',
        f'    <div class="card-badges">{badges}</div>',
        f'    <div class="card-name">{esc(c["name"])}</div>',
        f'    <div class="card-location">{build_location(c)}</div>',
        f'    <div class="card-specs">{build_specs(c)}</div>',
        f'    <div class="card-summary">{summary}{tip_html}</div>',
        f'    {build_footnote(c)}',
        f'  </div>',
        f'</div>',
    ])

# Default view (no filters) = flat, A→Z sorted list, no subregion header — matches live default exactly
sorted_courses = sorted(COURSES, key=sorted_name)
initial_cards_html = "\n".join(build_card(c) for c in sorted_courses)

# Embed full course JSON for client-side filtering (no fetch, no external dependency)
courses_json = json.dumps(COURSES, ensure_ascii=False)

CSS = r"""
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --cream: #faf7ea;
    --green: #0e7490;
    --black: #030712;
    --white: #ffffff;
    --ink: #000000;
    --muted: #6b6b6b;
    --border: #9ca3af;
    --pub: #155724;
    --semi: #6b4200;
    --resort: #0a2f5e;
    --priv: #541060;
    --helene: #7a1515;
  }

  html, body { height: auto; overflow: visible; }

  body { font-family: "PT Serif", Georgia, serif; background: var(--white); color: #000000; font-size: 18px; line-height: 1.6; -webkit-font-smoothing: antialiased; }

  .filter-wrap { background: var(--white); padding: 0; max-width: 1200px; margin: 0 auto; }
  .filter-bar { display: flex; gap: 12px; align-items: center; width: 100%; }
  .filter-select {
    font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 15px; font-weight: 400;
    padding: 10px 36px 10px 14px; border: 1px solid var(--black); border-radius: 5px;
    background: var(--white); color: #000000; cursor: pointer; flex: 1 1 0; min-width: 0; width: 0;
    overflow: hidden; text-overflow: ellipsis; appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23030712' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 12px center; transition: border-color .15s;
  }
  .filter-select:focus { outline: none; border-color: #000000; }
  .filter-select.active { border-color: #000000; background-color: #E0EFF0; }
  .filter-status { display: flex; align-items: center; padding: 14px 0 32px; font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; }
  .filter-status.filtered { padding-bottom: 32px; }
  .filter-reset { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: var(--green); text-decoration: underline; text-underline-offset: 3px; background: none; border: none; cursor: pointer; padding: 0; }

  @media (max-width: 700px) {
    .filter-bar { flex-direction: column; }
    .filter-select { width: 100%; flex: none; min-width: unset; }
    .filter-wrap { padding: 0; }
  }

  .subregion-header { max-width: 1200px; margin: 0 auto; padding: 32px 0 24px; }
  .subregion-header.filtered { padding-top: 8px; }
  .subregion-eyebrow { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--green); line-height: 24px; margin-bottom: 8px; }
  .subregion-title { font-family: "PT Serif", Georgia, serif; font-size: clamp(28px, 5vw, 56px); font-weight: 700; color: #000000; line-height: 1.1; margin-bottom: 10px; }
  .subregion-counties { font-size: 18px; line-height: 1.5; color: #000000; padding-bottom: 8px; }
  .subregion-vibe { font-size: 18px; line-height: 1.6; color: #000000; font-style: italic; padding-bottom: 20px; }

  .card-grid { max-width: 1200px; margin: 0 auto; padding: 0; display: grid; grid-template-columns: repeat(2, 1fr); column-gap: 40px; row-gap: 80px; }

  .card { background: var(--white); }

  .card-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
  .badge { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 10px; letter-spacing: .08em; text-transform: uppercase; padding: 6px 12px; border-radius: 2px; font-weight: 700; line-height: 1; display: inline-flex; align-items: center; justify-content: center; vertical-align: middle; }
  .badge.public { background: #d6edda; color: var(--pub); }
  .badge.semi { background: #fde8c8; color: var(--semi); }
  .badge.resort { background: #c8dcf5; color: var(--resort); }
  .badge.private { background: #eedaf0; color: var(--priv); }
  .badge.helene { background: #fad8d8; color: var(--helene); }

  .card-name { font-family: "PT Serif", Georgia, serif; font-size: 32px; font-weight: 700; color: #000000; line-height: 1.2; margin-bottom: 8px; text-wrap: balance; }

  .card-location { margin-top: 10px; margin-bottom: 20px; }
  .card-location-address { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; line-height: 1.65; }
  .card-location-contact { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; line-height: 1.65; }
  .card-location-contact a { color: var(--green); text-decoration: underline; text-underline-offset: 3px; }
  .card-location-contact a:hover { opacity: .7; }

  .card-specs { display: flex; margin-bottom: 18px; border: 1px solid #000000; border-radius: 2px; overflow: hidden; }
  .spec-item { flex: 1; padding: 10px 12px; border-right: 1px solid #000000; background: transparent; }
  .spec-item:last-child { border-right: none; }
  .spec-label { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; font-weight: 400; display: block; line-height: 1.5; }
  .spec-value { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 700; color: #000000; display: block; line-height: 1.5; }

  .card-summary { font-size: 18px; line-height: 1.6; color: #000000; margin-bottom: 0; }
  .card-summary em { font-style: italic; }

  .insider-tip { display: block; margin-top: 28px; font-size: 18px; line-height: 1.6; color: #000000; font-style: italic; }
  .insider-tip::before { content: "Insider tip"; display: block; font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 12px; font-style: normal; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--green); margin-bottom: 4px; }

  .card-footnote { margin-top: 16px; font-family: "PT Serif", Georgia, serif; font-size: 17px; color: #597C8F; line-height: 1.6; font-style: italic; }

  .prose-link { color: var(--green); text-decoration: underline; text-underline-offset: 3px; }
  .prose-link:hover { opacity: .7; }

  .empty-state { padding: 16px 0 48px; text-align: left; }
  .empty-state-headline { font-family: "PT Serif", Georgia, serif; font-size: clamp(28px, 4vw, 40px); font-weight: 700; color: #000000; margin-bottom: 12px; }
  .empty-state-body { font-family: "PT Serif", Georgia, serif; font-size: 18px; color: #000000; line-height: 1.6; }
  .empty-state-reset { display: inline-block; margin-top: 24px; font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--green); text-decoration: underline; text-underline-offset: 3px; background: none; border: none; cursor: pointer; padding: 0; }

  .site-footer { background: var(--cream); border-top: 1px solid var(--border); text-align: center; padding: 48px 0; font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.7; color: #000000; }
  .site-footer strong { color: #000000; }

  .card[data-hidden="true"] { display: none; }

  @media (max-width: 700px) {
    .card-grid { grid-template-columns: 1fr; padding: 0; column-gap: 0; row-gap: 64px; }
    .subregion-header { padding: 32px 0 20px; }
    .subregion-header.filtered { padding-top: 8px; }
    .subregion-title { font-size: 36px; }
    .card-name { font-size: 28px; }
  }
"""

HTML = f"""<!--
  WNC GOLF INSIDER — DIRECTORY EMBED (STATIC, SEO-INDEXABLE)
  Based on: live v5.53 embed
  Change: all {TOTAL} courses pre-rendered as static HTML at build time (no fetch()).
  Course data is embedded inline as JSON — filtering/sorting/Jump menu behave
  identically to v5.53, just reading from the embedded array instead of a network fetch.
  Visual output on initial load is byte-identical to the current live default state
  (flat, alphabetical, no subregion header) — this IS what v5.53 shows with no filters applied.
  To update: re-run build_static_directory_v2.py after editing wnc_courses.json, paste the output in.
  Built from wnc_courses.json — {TOTAL} courses.
-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=PT+Serif:ital,wght@0,400;0,700;1,400;1,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>{CSS}</style>

<script>
(function() {{
  function fixScroll() {{
    try {{
      var iframe = window.frameElement;
      if (!iframe) return;
      iframe.setAttribute('scrolling', 'no');
    }} catch(e) {{}}
  }}
  fixScroll();
  window.addEventListener('load', fixScroll);
  setTimeout(fixScroll, 1000);
  setTimeout(fixScroll, 3000);

  window.wncSetHeight = function() {{
    var root = document.getElementById('wnc-dir-root');
    if (!root) return;
    var h = root.getBoundingClientRect().height;
    try {{
      var iframe = window.frameElement;
      if (iframe) {{
        iframe.style.minHeight = '0';
        iframe.style.height = h + 'px';
      }}
    }} catch(e) {{}}
    try {{ window.parent.postMessage({{ wnc_embed_height: h }}, '*'); }} catch(e) {{}}
  }};
  window.addEventListener('load', function() {{ setTimeout(window.wncSetHeight, 100); setTimeout(window.wncSetHeight, 500); }});
  if (window.ResizeObserver) {{
    window.addEventListener('DOMContentLoaded', function() {{
      var root = document.getElementById('wnc-dir-root');
      if (root) new ResizeObserver(function() {{ window.wncSetHeight(); }}).observe(root);
    }});
  }}
}})();
</script>

<div id="wnc-dir-root">
  <div class="filter-wrap">
    <div class="filter-bar">
      <select class="filter-select" id="region-select">
        <option value="all">All Subregions</option>
        <option value="asheville-basin">Asheville Basin</option>
        <option value="high-country">High Country</option>
        <option value="hendersonville-plateau">Hendersonville Plateau</option>
        <option value="smoky-corridor">Smoky Mountain Corridor</option>
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
      <select class="filter-select" id="jump-select">
        <option value="">All Golf Courses</option>
      </select>
    </div>
    <div class="filter-status" id="filter-status">Showing {TOTAL} golf courses</div>
  </div>
  <div id="wnc-dir-content">
<div class="card-grid">
{initial_cards_html}
</div>
  </div>
</div>

<script>
(function() {{
  var ALL_COURSES = {courses_json};

  function esc(s) {{
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}

  function linkify(s) {{
    s = String(s || '');
    var emSlots = [];
    s = s.replace(/<em>([\\s\\S]*?)<\\/em>/g, function(_, inner) {{
      var idx = emSlots.length;
      emSlots.push(inner);
      return '\\x00em' + idx + '\\x00';
    }});
    s = s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    s = s.replace(
      /(?:https?:\\/\\/)?(?:www\\.)?([a-zA-Z0-9-]+(?:\\.[a-zA-Z]{{2,}})+(?:\\/[^\\s,;.!?]*[^\\s,;.!?)])?)/g,
      function(match) {{
        var href = /^https?:\\/\\//i.test(match) ? match : 'https://' + match;
        return '<a class="prose-link" href="' + href + '" target="_blank" rel="noopener">' + match + '</a>';
      }}
    );
    s = s.replace(/\\x00em(\\d+)\\x00/g, function(_, i) {{
      return '<em>' + esc(emSlots[parseInt(i, 10)]) + '</em>';
    }});
    return s;
  }}

  var BADGE_CLASSES  = {{ public: 'public', 'semi-private': 'semi', resort: 'resort', private: 'private' }};
  var ACCESS_LABELS  = {{ public: 'Public', 'semi-private': 'Semi-Private', resort: 'Resort', private: 'Private' }};

  var SUBREGIONS = [
    {{ slug: 'asheville-basin',        num: 1, title: 'Asheville Basin',              counties: 'Buncombe \\u00b7 Madison \\u00b7 Haywood',                                  vibe: 'The cultural and geographic heart of WNC golf \\u2014 Donald Ross municipal gems, resort marquee tracks, and elite private clubs within minutes of downtown.' }},
    {{ slug: 'high-country',           num: 2, title: 'High Country',                 counties: 'Watauga \\u00b7 Ashe \\u00b7 Avery \\u00b7 Mitchell \\u00b7 Yancey \\u00b7 Caldwell \\u00b7 Wilkes \\u00b7 Alleghany', vibe: 'The roof of WNC golf \\u2014 courses at 3,000\\u20135,000 feet where the air is thin, the views reach into Tennessee, and ball flights run long.' }},
    {{ slug: 'hendersonville-plateau', num: 3, title: 'Hendersonville Plateau',       counties: 'Henderson \\u00b7 Polk \\u00b7 Rutherford \\u00b7 McDowell \\u00b7 Burke',               vibe: 'The transition zone \\u2014 thermal-belt mountain golf with championship resort tracks, historic munis, and the most diverse mix of access types in the region.' }},
    {{ slug: 'smoky-corridor',         num: 4, title: 'Smoky Mountain Corridor', counties: 'Haywood \\u00b7 Swain \\u00b7 Jackson \\u00b7 Macon \\u00b7 Cherokee \\u00b7 Clay \\u00b7 Graham',   vibe: 'Fog-draped ridgelines, lakefront layouts, and the quietest courses in WNC. Golf here is unhurried by design.' }},
    {{ slug: 'highlands-plateau',       num: 5, title: 'Highlands Plateau',            counties: 'Transylvania \\u00b7 Jackson \\u00b7 Macon',                                  vibe: 'The Highlands-Cashiers-Sapphire triangle \\u2014 the most concentrated cluster of elite private golf in the eastern United States.' }},
    {{ slug: 'foothills',              num: 6, title: 'Foothills',                    counties: 'Rutherford \\u00b7 McDowell \\u00b7 Burke \\u00b7 Caldwell \\u00b7 Wilkes \\u00b7 Alleghany',    vibe: 'Where the mountains meet the piedmont \\u2014 championship public layouts, hidden community courses, and the best value green fees in WNC.' }}
  ];

  var ACCESS_TYPES = {{
    'public':       {{ title: 'Public',       vibe: 'Tee times open to everyone \\u2014 from local municipals to daily-fee mountain layouts with views that stop you mid-swing.' }},
    'semi-private': {{ title: 'Semi-Private',  vibe: 'Member-first clubs that open select tee times to the public. Often the best value in the region \\u2014 local knowledge gets you on.' }},
    'resort':       {{ title: 'Resort',        vibe: 'Courses tied to WNC\\u2019s premier lodges and destination properties. Green fees include the full mountain experience.' }},
    'private':      {{ title: 'Private',       vibe: 'Invitation and membership only, with very few exceptions. These are the benchmarks everything else is measured against.' }}
  }};

  var COMBO_HEADERS = {{
    'asheville-basin:public':           'The Ross munis and daily-fee tracks that make Asheville one of the most accessible golf cities in the South.',
    'asheville-basin:semi-private':     'A short list \\u2014 the Asheville Basin skews public and private, with few clubs in between.',
    'asheville-basin:resort':           'Resort-access tracks within striking distance of downtown. Grove Park sets the standard.',
    'asheville-basin:private':          'The most storied private clubs in WNC, clustered within minutes of downtown Asheville.',
    'high-country:public':              'High-altitude daily-fee golf with some of the longest ball flights in the eastern US.',
    'high-country:semi-private':        'Limited options at elevation that offer exceptional mountain value.',
    'high-country:resort':              'Resort golf at 3,000\\u20135,000 feet, where the fairways tilt and the views stretch into Tennessee.',
    'high-country:private':             'The private clubs that first defined mountain golf in North Carolina.',
    'hendersonville-plateau:public':    'The most accessible stretch of mountain golf in WNC with good value, varied terrain, and no attitude.',
    'hendersonville-plateau:semi-private': 'Semi-private clubs that offer a genuine local golf experience, no membership required.',
    'hendersonville-plateau:resort':    'Championship resort tracks in the thermal belt.',
    'hendersonville-plateau:private':   'Quiet, serious private golf in the shadow of the Blue Ridge mountains.',
    'smoky-corridor:public':            'Lakefront layouts and fog-draped valley courses \\u2014 unhurried golf at the edge of the national park.',
    'smoky-corridor:semi-private':      'Accessible mountain golf deep in the Smokies, where the courses are as quiet as the ridgelines above them.',
    'smoky-corridor:resort':            'Casino-adjacent resort golf and lodge-access tracks at the western edge of WNC.',
    'smoky-corridor:private':           'Private clubs here are few and exclusive \\u2014 deeply rooted in the communities around them.',
    'highlands-plateau:public':         'Rare in this zip code. The Highlands Plateau runs private by nature \\u2014 public access here is the exception.',
    'highlands-plateau:semi-private':   'A handful of semi-private options in the Highlands\\u2013Cashiers triangle, where private is the default.',
    'highlands-plateau:resort':         'Resort-access tracks of the Highlands Plateau \\u2014 golf as part of a broader luxury experience.',
    'highlands-plateau:private':        'The most concentrated cluster of elite private golf in the eastern US. You will need to know someone.',
    'foothills:public':                 'Championship-quality public golf at piedmont prices \\u2014 the best bang-for-green-fee in all of WNC.',
    'foothills:semi-private':           'Foothills semi-private clubs are community anchors \\u2014 open, welcoming, and easy on the wallet.',
    'foothills:resort':                 'Resort golf where the mountains flatten out \\u2014 wider fairways, lower elevation, different kind of challenge.',
    'foothills:private':                'The Foothills\\u2019 private clubs serve tight-knit communities where golf has been a local institution for decades.'
  }};

  function buildSpecs(c) {{
    if (c.yards || c.slope || c.rating || c.par) {{
      var items = '';
      if (c.par)    items += '<div class="spec-item"><span class="spec-label">Par</span><span class="spec-value">' + c.par + '</span></div>';
      if (c.yards)  items += '<div class="spec-item"><span class="spec-label">Yards</span><span class="spec-value">' + String(c.yards).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ',') + '</span></div>';
      if (c.rating) items += '<div class="spec-item"><span class="spec-label">Rating</span><span class="spec-value">' + c.rating + '</span></div>';
      if (c.slope)  items += '<div class="spec-item"><span class="spec-label">Slope</span><span class="spec-value">' + c.slope + '</span></div>';
      return items;
    }}
    return '<div class="spec-item spec-item--full"><span class="spec-label">Rating</span><span class="spec-value">Not rated</span></div>';
  }}

  function buildLocation(c) {{
    var addr = c.address || [c.city, c.county ? c.county + ' County' : '', 'NC'].filter(Boolean).join(', ');
    var addrHtml = '';
    if (addr) {{
      var lastComma = addr.lastIndexOf(', ');
      var secondLastComma = lastComma > 0 ? addr.lastIndexOf(', ', lastComma - 1) : -1;
      var splitAt = secondLastComma > -1 ? secondLastComma : lastComma;
      var line1 = splitAt > -1 ? addr.slice(0, splitAt) : addr;
      var line2 = splitAt > -1 ? addr.slice(splitAt + 2) : '';
      addrHtml = '<div class="card-location-address">'
        + esc(line1)
        + (line2 ? '<br>' + esc(line2) : '')
        + '</div>';
    }}

    var contactHtml = '';
    if (c.website && !c.website.startsWith('tel:')) {{
      var domain = c.website.replace(/https?:\\/\\//, '').replace(/\\/.*/, '').replace(/^www\\./, '');
      contactHtml += '<div class="card-location-contact"><a href="' + esc(c.website) + '" target="_blank">' + esc(domain) + '</a></div>';
    }}
    if (c.phone) {{
      var num = c.phone.replace('tel:', '').replace(/(\\d{{3}})(\\d{{3}})(\\d{{4}})/, '($1) $2-$3');
      contactHtml += '<div class="card-location-contact"><a href="' + esc(c.phone) + '">' + esc(num) + '</a></div>';
    }}

    return addrHtml + contactHtml;
  }}

  function buildFootnote(c) {{
    if (c.usga_rating_note) {{
      return '<div class="card-footnote">' + esc(c.usga_rating_note) + '</div>';
    }}
    return '';
  }}

  function buildCard(c) {{
    var badgeCls    = BADGE_CLASSES[c.access] || 'public';
    var accessLabel = ACCESS_LABELS[c.access]  || esc(c.access || '');
    var badges = '<span class="badge ' + badgeCls + '">' + accessLabel + '</span>';
    if (c.helene) badges += ' <span class="badge helene">Helene Impact</span>';
    if (c.closed) badges += ' <span class="badge helene">Temporarily Closed</span>';

    return [
      '<div class="card" data-access="' + badgeCls + '" data-region="' + esc(c.subregion || '') + '">',
      '  <div class="card-body">',
      '    <div class="card-badges">' + badges + '</div>',
      '    <div class="card-name">' + esc(c.name) + '</div>',
      '    <div class="card-location">' + buildLocation(c) + '</div>',
      '    <div class="card-specs">' + buildSpecs(c) + '</div>',
      '    <div class="card-summary">' + linkify(c.summary || '') + (c.insider_tip ? '<span class="insider-tip">' + linkify(c.insider_tip) + '</span>' : '') + '</div>',
      '    ' + buildFootnote(c),
      '  </div>',
      '</div>'
    ].join('\\n');
  }}

  function sortedName(c) {{
    return c.name.toLowerCase().replace(/^(the |a |an )/, '');
  }}

  function sortCourses(list) {{
    return list.slice().sort(function(a, b) {{
      return sortedName(a) < sortedName(b) ? -1 : sortedName(a) > sortedName(b) ? 1 : 0;
    }});
  }}

  function renderContent(courses, rf, af, isJump) {{
    var contentEl = document.getElementById('wnc-dir-content');
    var html;

    if (!courses.length) {{
      html = '<div class="empty-state">'
           + '<div class="empty-state-headline">No courses found.</div>'
           + '<div class="empty-state-body">No courses match your current filters.<br>Try adjusting your selection to explore more of the mountains.</div>'
           + '</div>';
    }} else if (isJump) {{
      html = '<div class="card-grid">' + sortCourses(courses).map(buildCard).join('\\n') + '</div>';
    }} else if (rf === 'all' && af === 'all') {{
      html = '<div class="card-grid">' + sortCourses(courses).map(buildCard).join('\\n') + '</div>';
    }} else if (rf !== 'all' && af !== 'all') {{
      var comboKey = rf + ':' + af;
      var comboVibe = COMBO_HEADERS[comboKey] || '';
      var comboRegion = SUBREGIONS.filter(function(r) {{ return r.slug === rf; }})[0];
      var comboRegionTitle = comboRegion ? comboRegion.title : '';
      var comboAccessLabel = ACCESS_LABELS[af] || '';
      var comboTitle = comboRegionTitle && comboAccessLabel ? comboRegionTitle + ' \\u00b7 ' + comboAccessLabel : '';
      var comboHeader = '<div class="subregion-header filtered">'
        + (comboTitle ? '<h2 class="subregion-title">' + esc(comboTitle) + '</h2>' : '')
        + (comboVibe ? '<div class="subregion-vibe">' + esc(comboVibe) + '</div>' : '')
        + '</div>';
      html = comboHeader + '<div class="card-grid">' + sortCourses(courses).map(buildCard).join('\\n') + '</div>';
    }} else if (rf !== 'all') {{
      var region = SUBREGIONS.filter(function(r) {{ return r.slug === rf; }})[0];
      var regionHeader = region
        ? '<div class="subregion-header filtered">'
          + '<h2 class="subregion-title">' + esc(region.title) + '</h2>'
          + '<div class="subregion-vibe">' + esc(region.vibe) + '</div>'
          + '</div>'
        : '';
      html = regionHeader + '<div class="card-grid">' + sortCourses(courses).map(buildCard).join('\\n') + '</div>';
    }} else {{
      var accessType = ACCESS_TYPES[af];
      var accessHeader = accessType
        ? '<div class="subregion-header filtered">'
          + '<h2 class="subregion-title">' + esc(accessType.title) + '</h2>'
          + '<div class="subregion-vibe">' + esc(accessType.vibe) + '</div>'
          + '</div>'
        : '';
      html = accessHeader + '<div class="card-grid">' + sortCourses(courses).map(buildCard).join('\\n') + '</div>';
    }}
    contentEl.innerHTML = html;
  }}

  function populateJumpMenu(courses) {{
    var jumpSel = document.getElementById('jump-select');
    if (!jumpSel) return;
    var current = jumpSel.value;
    while (jumpSel.options.length > 1) jumpSel.remove(1);
    sortCourses(courses).forEach(function(c) {{
      var opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name;
      jumpSel.appendChild(opt);
    }});
    if (current && courses.some(function(c) {{ return c.id === current; }})) {{
      jumpSel.value = current;
    }} else {{
      jumpSel.value = '';
    }}
  }}

  function initFilters() {{
    var rSel     = document.getElementById('region-select');
    var aSel     = document.getElementById('access-select');
    var jumpSel  = document.getElementById('jump-select');
    var statusEl = document.getElementById('filter-status');

    var jumpCourseId = null;

    function applyFilters() {{
      var rf = rSel.value;
      var af = aSel.value;

      rSel.className    = 'filter-select' + (rf !== 'all' ? ' active' : '');
      aSel.className    = 'filter-select' + (af !== 'all' ? ' active' : '');
      if (jumpSel) jumpSel.className = 'filter-select' + (jumpCourseId ? ' active' : '');

      var baseFiltered = (ALL_COURSES || []).filter(function(c) {{
        var matchRegion = rf === 'all' || c.subregion === rf;
        var matchAccess = af === 'all' || c.access === af;
        return matchRegion && matchAccess;
      }});

      populateJumpMenu(baseFiltered);

      var displayCourses = jumpCourseId
        ? baseFiltered.filter(function(c) {{ return c.id === jumpCourseId; }})
        : baseFiltered;

      var displayRf = rf;
      if (jumpCourseId && displayCourses.length) {{
        displayRf = displayCourses[0].subregion;
      }}

      renderContent(displayCourses, displayRf, af, !!jumpCourseId);

      var visible   = displayCourses.length;
      var anyFilter = rf !== 'all' || af !== 'all' || !!jumpCourseId;
      var subregionFiltered = rf !== 'all' || !!jumpCourseId;
      statusEl.className = subregionFiltered ? 'filter-status filtered' : 'filter-status';

      var resetBtn = anyFilter
        ? ' <span style="color:var(--muted);margin:0 10px">&middot;</span> <button class="filter-reset" id="filter-reset-btn">Reset</button>'
        : '';

      var label = 'Showing ' + visible + ' golf course' + (visible !== 1 ? 's' : '');
      statusEl.innerHTML = '<span>' + label + '</span>' + resetBtn;

      if (anyFilter) {{
        document.getElementById('filter-reset-btn').addEventListener('click', function() {{
          rSel.value  = 'all';
          aSel.value  = 'all';
          jumpCourseId = null;
          if (jumpSel) jumpSel.value = '';
          updateParentUrl(null, null, null);
          applyFilters();
        }});
      }}

      setTimeout(function() {{ if (window.wncSetHeight) window.wncSetHeight(); }}, 50);
    }}

    // Keep the parent page's URL in sync with the current filter state.
    // A specific course (Jump to) is encoded as a hash: #wade-hampton
    // Region/access filters (without a specific course) are encoded as query
    // params: ?region=highlands-plateau&access=private
    // Uses replaceState so it doesn't spam the browser's back-button history.
    function updateParentUrl(rf, af, courseId) {{
      try {{
        var base = window.parent.location.pathname;
        var params = [];
        if (courseId) {{
          params.push('course=' + encodeURIComponent(courseId));
        }} else {{
          if (rf && rf !== 'all') params.push('region=' + encodeURIComponent(rf));
          if (af && af !== 'all') params.push('access=' + encodeURIComponent(af));
        }}
        var newUrl = base + (params.length ? '?' + params.join('&') : '');
        window.parent.history.replaceState(null, '', newUrl);
        lastKnownHref = window.parent.location.href;
      }} catch (e) {{
        // Cross-origin or other restriction — filtering still works locally,
        // the URL just won't reflect the selection.
      }}
    }}

    rSel.addEventListener('change', function() {{
      jumpCourseId = null;
      if (jumpSel) jumpSel.value = '';
      updateParentUrl(rSel.value, aSel.value, null);
      applyFilters();
    }});

    aSel.addEventListener('change', function() {{
      jumpCourseId = null;
      if (jumpSel) jumpSel.value = '';
      updateParentUrl(rSel.value, aSel.value, null);
      applyFilters();
    }});

    if (jumpSel) {{
      jumpSel.addEventListener('change', function() {{
        var selectedId = jumpSel.value;
        if (!selectedId) {{
          jumpCourseId = null;
          updateParentUrl(rSel.value, aSel.value, null);
          applyFilters();
          return;
        }}
        var course = (ALL_COURSES || []).find(function(c) {{ return c.id === selectedId; }});
        if (course) {{
          rSel.value = course.subregion || 'all';
          aSel.value = course.access    || 'all';
          jumpCourseId = selectedId;
          updateParentUrl(null, null, selectedId);
          applyFilters();
        }}
      }});
    }}

    // Deep-link support: the srcdoc iframe has no `sandbox` attribute, so it is
    // treated as same-origin with the parent page — window.parent.location is
    // readable directly, no postMessage handshake required.
    //   /course-directory?course=wade-hampton                  -> jumps to one course
    //   /course-directory?region=highlands-plateau            -> filters by region
    //   /course-directory?access=private                       -> filters by access
    //   /course-directory?region=highlands-plateau&access=private -> both
    //
    // A query string (not a hash) is used deliberately: Beehiiv's site nav is
    // a client-side (Remix) router, and like most JS routers it treats a hash
    // difference as browser-native scroll-anchor territory and ignores it —
    // clicking a nav link back to the bare page while a #course-name was in
    // the URL was a no-op that never touched the address bar at all. Search
    // params don't have that problem; routers generally do react to them.
    var VALID_REGIONS = SUBREGIONS.map(function(r) {{ return r.slug; }});
    var VALID_ACCESS  = Object.keys(ACCESS_LABELS);

    function stateFromQuery() {{
      try {{
        var params = new URLSearchParams(window.parent.location.search || '');
        var courseId = params.get('course');
        var region   = params.get('region');
        var access   = params.get('access');
        var course   = courseId ? (ALL_COURSES || []).find(function(c) {{ return c.id === courseId; }}) : null;
        return {{
          course: course || null,
          region: (region && VALID_REGIONS.indexOf(region) > -1) ? region : null,
          access: (access && VALID_ACCESS.indexOf(access)  > -1) ? access : null
        }};
      }} catch (e) {{
        return {{ course: null, region: null, access: null }};
      }}
    }}

    function applyDeepLink(course) {{
      if (!course) return false;
      rSel.value = course.subregion || 'all';
      aSel.value = course.access    || 'all';
      jumpCourseId = course.id;
      if (jumpSel) jumpSel.value = course.id;
      return true;
    }}

    // Initial load: a specific course takes priority over region/access
    // params (a course implies both anyway). If there's no course, fall
    // back to whatever region/access came in via query params.
    var initialState = stateFromQuery();
    if (initialState.course) {{
      applyDeepLink(initialState.course);
    }} else {{
      if (initialState.region) rSel.value = initialState.region;
      if (initialState.access) aSel.value = initialState.access;
    }}

    // Sync FROM the parent URL whenever it changes externally (nav clicks,
    // back/forward, a visitor editing the address bar, etc.) — but NOT when
    // *we* just wrote it ourselves via updateParentUrl, which already keeps
    // lastKnownHref in sync to avoid redundant re-renders. Polling (rather
    // than relying on an event) is what actually catches Remix's pushState-
    // based route transitions, which don't fire hashchange or popstate.
    var lastKnownHref = '';
    try {{ lastKnownHref = window.parent.location.href; }} catch (e) {{}}

    function syncFromParentUrl() {{
      var currentHref = '';
      try {{ currentHref = window.parent.location.href; }} catch (e) {{ return; }}
      if (currentHref === lastKnownHref) return;
      lastKnownHref = currentHref;

      var state = stateFromQuery();
      if (state.course) {{
        applyDeepLink(state.course);
      }} else {{
        jumpCourseId = null;
        if (jumpSel) jumpSel.value = '';
        rSel.value = state.region || 'all';
        aSel.value = state.access || 'all';
      }}
      applyFilters();
    }}

    try {{
      setInterval(syncFromParentUrl, 400);
    }} catch (e) {{}}

    applyFilters();
  }}

  initFilters();
}})();
</script>
"""

with open('/home/claude/wnc_static_directory_v2.0.html', 'w') as f:
    f.write(HTML)

print(f"Built: {len(HTML):,} chars, {TOTAL} courses")
