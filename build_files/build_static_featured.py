import json, re

with open('/home/claude/wnc_courses.json') as f:
    DATA = json.load(f)

COURSES = DATA['courses']
COURSES_BY_ID = {c['id']: c for c in COURSES}

FEATURED_IDS = [
    'omni-grove-park',
    'broadmoor-golf-links',
    'laurel-ridge-cc',
    'sequoyah-national'
]

IMAGE_BASE = 'https://raw.githubusercontent.com/davebedingfield/wnc-golf-data/main/images/'
COURSE_IMAGES = {
    'omni-grove-park':       IMAGE_BASE + 'grove_park_wc_featured.jpg',
    'sequoyah-national':     IMAGE_BASE + 'sequoyah_national_wc_featured.jpg',
    'laurel-ridge-cc':       IMAGE_BASE + 'laurel_ridge_wc_featured.jpg',
    'broadmoor-golf-links':  IMAGE_BASE + 'broadmoor_wc_featured.jpg'
}

BADGE_CLASSES = {"public": "public", "semi-private": "semi", "resort": "resort", "private": "private"}
ACCESS_LABELS = {"public": "Public", "semi-private": "Semi-Private", "resort": "Resort", "private": "Private"}

# Fail loudly rather than silently rendering fewer than 4 cards.
missing = [fid for fid in FEATURED_IDS if fid not in COURSES_BY_ID]
if missing:
    raise SystemExit(f"FEATURED_IDS not found in wnc_courses.json: {missing}")

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

def build_image(course_id, name):
    src = COURSE_IMAGES.get(course_id)
    if not src:
        return ''
    return f'<img class="card-image" src="{src}" alt="{esc(name)}" loading="lazy">'

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
        '<div class="card">',
        f'  <div class="card-badges">{badges}</div>',
        f'  <div class="card-name">{esc(c["name"])}</div>',
        f'  <div class="card-location">{build_location(c)}</div>',
        f'  {build_image(c["id"], c["name"])}',
        f'  <div class="card-specs">{build_specs(c)}</div>',
        f'  <div class="card-summary">{summary}{tip_html}</div>',
        f'  {build_footnote(c)}',
        '</div>',
    ])

featured_courses = [COURSES_BY_ID[fid] for fid in FEATURED_IDS]
cards_html = "\n".join(build_card(c) for c in featured_courses)

CSS = r"""
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --cream:  #faf4eb;
  --green:  #0e7490;
  --black:  #030712;
  --white:  #faf4eb;
  --ink:    #1a1a1a;
  --muted:  #6b6b6b;
  --border: #9ca3af;
  --pub:    #155724;
  --semi:   #6b4200;
  --resort: #0a2f5e;
  --priv:   #541060;
  --helene: #7a1515;
}

body { font-family: "PT Serif", Georgia, serif; background: var(--white); color: #000000; font-size: 18px; line-height: 1.6; -webkit-font-smoothing: antialiased; }

/* Card grid — 2x2 */
.featured-grid { max-width: 1200px; margin: 0 auto; padding: 0; display: grid; grid-template-columns: repeat(2, 1fr); column-gap: 40px; row-gap: 80px; }

/* Card */
.card { background: var(--white); }

/* Course image */
.card-image { width: 100%; height: 340px; object-fit: cover; border-radius: 2px; display: block; margin-bottom: 20px; }

/* Badges */
.card-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.badge { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 10px; letter-spacing: .08em; text-transform: uppercase; padding: 6px 12px; border-radius: 2px; font-weight: 700; line-height: 1; display: inline-flex; align-items: center; justify-content: center; vertical-align: middle; }
.badge.public  { background: #d6edda; color: var(--pub); }
.badge.semi    { background: #fde8c8; color: var(--semi); }
.badge.resort  { background: #c8dcf5; color: var(--resort); }
.badge.private { background: #eedaf0; color: var(--priv); }
.badge.helene  { background: #fad8d8; color: var(--helene); }

/* Course name */
.card-name { font-family: "PT Serif", Georgia, serif; font-size: 32px; font-weight: 700; color: #000000; line-height: 1.2; margin-bottom: 8px; text-wrap: balance; }

/* Address + links */
.card-location { margin-top: 10px; margin-bottom: 20px; }
.card-location-address { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; line-height: 1.65; }
.card-location-contact { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; line-height: 1.65; }
.card-location-contact a { color: var(--green); text-decoration: underline; text-underline-offset: 3px; }
.card-location-contact a:hover { opacity: .7; }

/* Specs */
.card-specs { display: flex; margin-bottom: 18px; border: 1px solid #000000; border-radius: 2px; overflow: hidden; }
.spec-item { flex: 1; padding: 10px 12px; border-right: 1px solid #000000; background: transparent; }
.spec-item:last-child { border-right: none; }
.spec-label { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; color: #000000; font-weight: 400; display: block; line-height: 1.5; }
.spec-value { font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 700; color: #000000; display: block; line-height: 1.5; }

/* Summary */
.card-summary { font-size: 18px; line-height: 1.6; color: #000000; margin-bottom: 0; }
.card-summary em { font-style: italic; }

/* Insider tip */
.insider-tip { display: block; margin-top: 28px; font-size: 18px; line-height: 1.6; color: #000000; font-style: italic; }
.insider-tip::before { content: "Insider tip"; display: block; font-family: "Inter", Helvetica, Arial, sans-serif; font-size: 12px; font-style: normal; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--green); margin-bottom: 4px; }

/* Footnote */
.card-footnote { margin-top: 16px; font-family: "PT Serif", Georgia, serif; font-size: 17px; color: #597C8F; line-height: 1.6; font-style: italic; }

/* Inline prose links */
.prose-link { color: var(--green); text-decoration: underline; text-underline-offset: 3px; }
.prose-link:hover { opacity: .7; }

@media (max-width: 700px) {
  .featured-grid { grid-template-columns: 1fr; padding: 0; column-gap: 0; row-gap: 64px; }
  .card-name { font-size: 28px; }
  .card-image { height: 240px; }
}
"""

HTML = f"""<!--
  WNC GOLF INSIDER — FEATURED COURSES EMBED (STATIC, SEO-INDEXABLE)
  Based on: live wnc_featured_embed_v2_31.html
  Change: all 4 featured course cards pre-rendered as static HTML at build
  time (no fetch()). Course data is baked in from wnc_courses.json at build
  time — no network dependency, no loading state, nothing for a crawler to
  miss.
  Paste into Beehiiv: Home page -> Featured section -> Embed block -> Code tab
  Featured IDs: {", ".join(FEATURED_IDS)}
  To update: edit FEATURED_IDS in build_static_featured.py to swap courses,
  or re-run after wnc_courses.json changes to refresh card content. Paste
  the output in.
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
}})();
</script>

<div id="wnc-featured-root">
  <div class="featured-grid" id="feat-grid">
{cards_html}
  </div>
</div>
"""

with open('/home/claude/wnc_static_featured_v1.0.html', 'w') as f:
    f.write(HTML)

print(f"Built: {len(HTML):,} chars, {len(featured_courses)} featured courses")
