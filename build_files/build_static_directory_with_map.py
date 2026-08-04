"""
Builds wnc_directory_with_map_YYYY-MM-DD.html from wnc_courses.json.

Architecture: this does NOT regenerate the Leaflet map, CSS, clustering,
popup, or zoom-control logic from scratch. That code is complex, hand-tuned,
and doesn't depend on course data content -- only on the course data VALUES,
which are injected via placeholders. Rewriting ~800 lines of map logic in
Python on every run would be needless risk for zero benefit.

Instead: wnc_directory_with_map_template.html (checked in alongside this
script) is the full file with three placeholders:
  __WNC_CARDS__              -> pre-rendered card HTML (flat, alphabetical)
  __WNC_ALL_COURSES_JSON__   -> the embedded course data array
  __WNC_COURSE_COUNT__       -> course count (appears in 2 places)
  __WNC_VERSION_DATE__       -> today's date, header comment only

This script fills those in. It does NOT touch the map/CSS/JS logic at all --
that only changes if someone edits the template directly (a Path B change,
same as the plain directory), in which case wnc_directory_with_map_template.html
needs updating and this script re-validated against it.

If the template's structure changes (e.g. the card-grid or ALL_COURSES
markers move), the placeholder substitution below will silently no-op rather
than error -- the validation step at the bottom checks for this.
"""

import json, re, datetime

with open('/home/claude/wnc_courses.json', encoding='utf-8') as f:
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

# Default view (no filters) = flat, A→Z sorted list — same as the plain directory
sorted_courses = sorted(COURSES, key=sorted_name)
cards_html = "\n".join(build_card(c) for c in sorted_courses)

courses_json = json.dumps(COURSES, ensure_ascii=False)

today = datetime.date.today().isoformat()

with open('/home/claude/wnc_directory_with_map_template.html', encoding='utf-8') as f:
    template = f.read()

output = template
output = output.replace('__WNC_CARDS__', cards_html)
output = output.replace('__WNC_ALL_COURSES_JSON__', courses_json)
output = output.replace('__WNC_COURSE_COUNT__', str(TOTAL))
output = output.replace('__WNC_VERSION_DATE__', today)

# Fail loudly if any placeholder didn't get replaced -- means the template
# structure drifted from what this script expects.
remaining = re.findall(r'__WNC_[A-Z_]+__', output)
if remaining:
    raise SystemExit(f"Unreplaced placeholders remain: {remaining} -- template may have drifted, check manually before using this output.")

out_path = f'/home/claude/wnc_directory_with_map_{today}.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Built: {out_path}  ({len(output):,} chars, {TOTAL} courses)")
