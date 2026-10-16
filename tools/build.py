#!/usr/bin/env python3
"""Builds caringcompanionsoklahoma.com (static pages, no framework).

Edit CONFIG below, then run:  python3 tools/build.py
Every value left as None shows on the page as a highlighted placeholder,
and `python3 tools/build.py --check` lists what is still missing.

GO-LIVE RULE: Oklahoma (OAC 310:662-8-1) forbids advertising a sitter or
companion service before the OSDH license is issued. Keep PREVIEW = True
(noindex, robots disallow, preview banner) until the license is in hand.
"""
import html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GUIDE_SERVICES_LINE = '  <p style="margin-top:18px"><b>Caring for someone with dementia?</b> Medicare\'s GUIDE program may pay for respite visits. <a href="medicare-guide.html">See who qualifies</a></p>'
GUIDE_PRICING_LINE = '<p>Regular companion care is paid privately; we don\'t bill Medicaid. For families living with dementia, Medicare\'s <a href="medicare-guide.html">GUIDE program</a> may cover respite visits.</p>'
GUIDE_CHECKBOX = '      <label><input type="checkbox" name="interests" value="guide"> Medicare GUIDE respite</label>\n'

CONFIG = {
    "PREVIEW": False,                    # live since 2026-10-16 (licensed; opening June 2027)
    "OPENING": "June 2027",             # licensed; visits start then
    "GUIDE": True,                       # Oklahoma GUIDE coverage confirmed 2026-10-16
    "DOMAIN": "https://caringcompanionsoklahoma.com",
    "PHONE": "(405) 500-1758",
    "AFTER_HOURS_PHONE": "(405) 500-1758",         # license requires one, answered outside office hours
    "EMAIL": None,                      # e.g. "mustang@mo-care.com"
    "STREET": None,                     # public office, not a home (OSDH rule)
    "CITY_STATE_ZIP": "Mustang, OK 73064",
    "RATE": "$30",                       # hourly companion rate, e.g. "$30"
    "MIN_VISIT": "4 hours",                  # e.g. "4 hours"
    "MIN_WEEK": "4 hours",                   # e.g. "8 hours"
    "LICENSE_NO": None,                 # OSDH license number
    "APPLY_URL": None,                  # where caregivers apply
    "FORM_ENDPOINT": None,              # lead-intake URL once the Hub knows Oklahoma
    "FORM_TOKEN": None,
}

MISSING = []

def v(key, shown=None):
    """Config value as safe HTML, or a visible placeholder."""
    val = CONFIG.get(key)
    if val:
        return html.escape(val)
    MISSING.append(key)
    label = shown or key.replace("_", " ").title()
    return f'<span class="ph" title="To fill in before go-live">{label}</span>'

def phone_href():
    p = CONFIG.get("PHONE")
    return "tel:+1" + "".join(c for c in p if c.isdigit()) if p else "contact.html"

def addr():
    """Street (if we have it) + city line; never a blank placeholder once live."""
    city = html.escape(CONFIG["CITY_STATE_ZIP"])
    if CONFIG.get("STREET"):
        return f'{html.escape(CONFIG["STREET"])}<br>{city}'
    return f'{v("STREET", "Office street address")}<br>{city}' if CONFIG["PREVIEW"] else city

def license_line():
    base = "Licensed by the Oklahoma State Department of Health as a Sitter or Companion Service"
    if CONFIG.get("LICENSE_NO"):
        return f'{base}, license {html.escape(CONFIG["LICENSE_NO"])}.'
    return f'{base}, license {v("LICENSE_NO", "license #")}.' if CONFIG["PREVIEW"] else base + "."

def email_dd():
    if CONFIG.get("EMAIL") or CONFIG["PREVIEW"]:
        return f'{email_dd()}'
    return ""

def or_email():
    if CONFIG.get("EMAIL") or CONFIG["PREVIEW"]:
        return f' or email {v("EMAIL", "email address")}'
    return ""

def icon(name, cls="icon"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="assets/icons.svg#{name}"/></svg>'

MARK = '<img class="logo" src="assets/cc-logo.png" alt="Caring Companions" width="800" height="206">'

NAV = [
    ("Care", [
        ("services.html", "What we do", "Companionship, meals, errands, rides"),
        ("index.html#good-day-club", "The Good Day Club", "More good years at home"),
        ("outings.html", "Good days out", "Outings near you"),
        ("medicare-guide.html", "Medicare GUIDE respite", "Dementia respite Medicare may cover"),
        ("getting-started.html", "Getting started", "From first call to first visit"),
    ]),
    ("pricing.html", "Pricing"),
    ("service-area.html", "Service area"),
    ("resources.html", "Resources"),
    ("About", [
        ("about.html", "Our story", "A family company since 2017"),
        ("contact.html", "Contact", "Call or send us a note"),
        ("join.html", "Join the opening list", "Opening June 2027"),
    ]),
]

def schema(page):
    if page != "index.html":
        return ""
    data = {
        "@context": "https://schema.org", "@type": "LocalBusiness",
        "name": "Caring Companions Oklahoma",
        "description": "Weekday companion care for older adults in Mustang, Oklahoma and nearby towns: companionship, meals, light housekeeping, errands, rides and seated exercise. Opening " + CONFIG["OPENING"] + ".",
        "url": CONFIG["DOMAIN"] + "/",
        "logo": CONFIG["DOMAIN"] + "/assets/cc-logo.png",
        "image": CONFIG["DOMAIN"] + "/assets/photos/hero-caregiver.jpg",
        "priceRange": (CONFIG.get("RATE") or "") + "/hour",
        "address": {"@type": "PostalAddress", "addressLocality": "Mustang", "addressRegion": "OK", "postalCode": "73064", "addressCountry": "US"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "18:00"}],
        "areaServed": [{"@type": "City", "name": t + ", OK"} for t in ["Mustang", "Yukon", "Tuttle", "El Reno", "Piedmont", "Bethany", "Nichols Hills", "Oklahoma City"]],
        "parentOrganization": {"@type": "Organization", "name": "Caring Companions", "url": "https://mo-care.com/"},
    }
    if CONFIG.get("PHONE"):
        data["telephone"] = "+1-" + "-".join([CONFIG["PHONE"][1:4], CONFIG["PHONE"][6:9], CONFIG["PHONE"][10:14]])
    if CONFIG.get("STREET"):
        data["address"]["streetAddress"] = CONFIG["STREET"]
    return '<script type="application/ld+json">' + json.dumps(data) + '</script>\n'

def head(page, title, desc):
    robots = '<meta name="robots" content="noindex, nofollow">\n' if CONFIG["PREVIEW"] else ""
    canon = CONFIG["DOMAIN"] + "/" + ("" if page == "index.html" else page.replace(".html", ""))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{'<base href="/">' if page == "404.html" else ""}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{robots}<link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{CONFIG["DOMAIN"]}/assets/photos/hero-caregiver.jpg">
<meta property="og:logo" content="{CONFIG["DOMAIN"]}/assets/cc-logo.png">
<link rel="icon" href="assets/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/app-preview.css">
{schema(page)}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''

def header(page):
    bar = (f'<div class="open-bar">Opening in Mustang in {CONFIG["OPENING"]}. <a href="join.html">Join the opening list</a><span class="hide-sm">, <button type="button" data-app-preview>see how booking will work</button>,</span> or <a href="careers.html">apply to join our team</a>.</div>\n')
    bar += ('<div class="preview-bar"><b>Preview only.</b> Not yet published. '
           'Highlighted items are still to be filled in.</div>\n') if CONFIG["PREVIEW"] else ""
    current = ' aria-current="page"'
    parts = []
    for n, item in enumerate(NAV):
        if isinstance(item[1], list):
            label, kids = item
            if label == "Care" and not CONFIG["GUIDE"]:
                kids = [k for k in kids if k[0] != "medicare-guide.html"]
            here = any(k[0] == page for k in kids)
            items = "".join(f'<a href="{h}"{current if h == page else ""}><b>{t}</b><small>{sub}</small></a>' for h, t, sub in kids)
            parts.append(f'<div class="nav-group"><button type="button" class="nav-top{" is-here" if here else ""}" aria-expanded="false" aria-controls="dd{n}">{label}<i class="caret" aria-hidden="true"></i></button>'
                         f'<div class="nav-dd" id="dd{n}">{items}</div></div>')
        else:
            href, label = item
            parts.append(f'<a class="nav-top" href="{href}"{current if href == page else ""}>{label}</a>')
    parts.append(f'<a class="nav-top nav-hiring" href="careers.html"{current if page == "careers.html" else ""}>We\'re hiring</a>')
    links = "\n    ".join(parts)
    return f'''{bar}<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="index.html" aria-label="Caring Companions Oklahoma, home">{MARK}
      <span class="brand-sub"><span class="sub-long">Companion Care<br></span>Mustang, Oklahoma</span></a>
    <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span></button>
    <nav class="nav" id="nav" aria-label="Main">
    {links}
    <a class="nav-phone" href="{phone_href()}">{v("PHONE", "(405) phone")}</a>
    <a class="btn" href="join.html">Join the list</a>
    </nav>
  </div>
</header>
<main id="main">
'''

def footer():
    return f'''</main>
<footer class="site-footer">
  <div class="shell">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">Caring Companions Oklahoma</div>
        <p>Companion care for older adults in Mustang and nearby towns. Part of the Caring Companions family, caring for families since 2017.</p>
        <p>{addr()}</p>
      </div>
      <div>
        <h4>Companion care</h4>
        <ul>
          <li><a href="services.html">What we do</a></li>
          <li><a href="pricing.html">Pricing</a></li>
          <li><a href="getting-started.html">Getting started</a></li>
          <li><a href="service-area.html">Service area</a></li>
{'          <li><a href="medicare-guide.html">Medicare GUIDE respite</a></li>' + chr(10) if CONFIG["GUIDE"] else ""}          <li><a href="outings.html">Good days out</a></li>
          <li><a href="resources.html">Family resources</a></li>
        </ul>
      </div>
      <div>
        <h4>About us</h4>
        <ul>
          <li><a href="about.html">Our story</a></li>
          <li><a href="careers.html">Careers</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="https://mo-care.com/">Caring Companions Missouri</a></li>
        </ul>
      </div>
      <div>
        <h4>Talk to us</h4>
        <ul>
          <li><a href="{phone_href()}">{v("PHONE", "(405) phone")}</a></li>
          <li>Monday to Friday, 8am to 6pm</li>
          <li>After hours: {v("AFTER_HOURS_PHONE", "after-hours phone")}</li>
        </ul>
      </div>
    </div>
    <p class="footer-towns">Companion care in <a href="companion-care-mustang-ok.html">Mustang</a> &middot; <a href="companion-care-yukon-ok.html">Yukon</a> &middot; <a href="companion-care-tuttle-ok.html">Tuttle</a> &middot; <a href="companion-care-el-reno-ok.html">El Reno</a> &middot; <a href="companion-care-piedmont-ok.html">Piedmont</a> &middot; <a href="companion-care-bethany-ok.html">Bethany</a> &middot; <a href="companion-care-nichols-hills-ok.html">Nichols Hills</a> &middot; <a href="companion-care-oklahoma-city-ok.html">Oklahoma City</a></p>
    <div class="footer-legal">
      <span>{license_line()}</span>
      <span>We provide companion care only. Our caregivers do not provide hands-on personal care or medical care.</span>
      <span>© 2026 Caring Companions. All rights reserved.</span>
    </div>
  </div>
</footer>
<div class="callbar">
  <a class="btn btn-outline" href="{phone_href()}">{icon("i-phone", "")} Call us</a>
  <a class="btn" href="join.html">Join the list</a>
</div>
<script src="assets/site.js"></script>
<script src="assets/app-preview.js" defer></script>
<script>window.JOIN_CONFIG = {json.dumps({"site": "oklahoma", "fallback": ("Please call " + CONFIG["PHONE"] + ".") if CONFIG.get("PHONE") else "Please call or email us instead."})};</script>
<script src="assets/join.js" defer></script>
</body>
</html>
'''

def cta_band(title="Be one of our first families.",
             text=f"We open in Mustang in {CONFIG['OPENING']}. Join the opening list and we'll be in touch as opening gets closer, or take a look at how booking will work."):
    return f'''<section class="section tight"><div class="shell">
  <div class="cta-band">
    <h2>{title}</h2>
    <p>{text}</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn btn-light" href="join.html">Join the opening list</a>
      <button type="button" class="btn btn-outline" style="color:#fff;border-color:#fff" data-app-preview>See how booking works</button>
    </div>
  </div>
</div></section>
'''

SERVICES = [
    ("i-chat", "Companionship", "Conversation, cards and puzzles, a walk to the mailbox, looking through old photos together. Someone who shows up, every time, and is glad to be there."),
    ("i-home", "Light housekeeping", "Dishes, laundry, tidying the rooms they use, changing bed linens, taking out the trash. The house stays the way they like it."),
    ("i-bowl", "Meal preparation", "Planning and cooking meals they enjoy, following any diet their doctor has given them, and sitting down to eat together."),
    ("i-bag", "Errands and shopping", "Groceries, the pharmacy pickup, the post office. Done for them, or with them if they'd like to get out."),
    ("i-car", "Rides to appointments", "A caregiver drives them to the doctor, the salon, church or lunch with a friend, waits, and brings them home."),
    ("i-strength", "Seated exercise", "A guided routine done sitting down, to keep strength, balance and energy up. Your caregiver leads it and does it right alongside them."),
    ("i-clock", "Medication reminders", "A reminder at the right time, every visit, so medications get taken on schedule. Reminders only; caregivers don't handle or set up medications."),
    ("i-heart-honey", "Respite for family", "Time off for the family member who does most of the caregiving. Go to work, run errands or rest, knowing someone is there."),
]

HT_CARD = f'''<div class="card tv-card">
  <div>{icon("i-tv")}</div>
  <div>
    <p class="kicker" style="margin-bottom:6px">Add-on service</p>
    <h3>HomeTogether TV</h3>
    <p>Family video calls right on their TV, plus camera-free sensors for gentle, passive safety monitoring. It keeps everyone connected on the days between visits, without taking away privacy or independence.</p>
    <p><b>$99 a month.</b> Free shipping and a 30-day money-back guarantee. <a href="https://tryhometogether.com/">Learn more at tryhometogether.com</a></p>
  </div>
</div>'''

NOT_DONE = [
    "Bathing, showering or help getting dressed",
    "Toileting or incontinence care",
    "Lifting, transfers or help getting in and out of bed",
    "Handling, sorting or giving medications",
    "Any nursing or medical care",
]

def page_index():
    cards = "\n".join(
        f'<a class="card card-link" href="services.html">{icon(i)}<h3>{t}</h3><p>{d}</p></a>'
        for i, t, d in SERVICES[:6])
    return f'''<section class="hero"><div class="shell hero-grid">
  <div>
    <p class="kicker">Weekday companion care in Mustang, Oklahoma <span class="open-chip">Opening {CONFIG["OPENING"]}</span></p>
    <h1>While you're at work, they're not alone.</h1>
    <p class="lede">A regular companion for Mom or Dad, Monday to Friday between 8 and 6. Good company, a hot lunch, the errands done and a ride to the doctor, so they stay independent longer and the workday stops being the part you worry about.</p>
    <div class="btn-row">
      <a class="btn" href="join.html">{icon("i-calendar", "")} Join the opening list</a>
      <a class="btn btn-outline" href="{phone_href()}">{icon("i-phone", "")} Call {v("PHONE", "(405) phone")}</a>
    </div>
    <ul class="trust-row">
      <li>{icon("i-clock", "")} Monday to Friday, 8am to 6pm</li>
      <li>{icon("i-phone", "")} Our office is open during every visit</li>
      <li>{icon("i-shield", "")} Fingerprint background checks</li>
    </ul>
  </div>
  <div class="hero-img"><picture><source srcset="assets/photos/hero-caregiver.webp" type="image/webp"><img src="assets/photos/hero-caregiver.jpg" alt="A caregiver and an older woman holding hands and laughing on a sofa" width="1100" height="733" fetchpriority="high"></picture></div>
</div></section>

<section class="section" id="good-day-club"><div class="shell">
  <span class="gdc-badge"><svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#FBEFD9" stroke="#C17A12" stroke-width="1.5"/><circle cx="16" cy="17" r="5.2" fill="#F0A63A" stroke="#0D365F" stroke-width="1.4"/><path d="M16 6.5v3M7.8 9.8l2.1 2.1M24.2 9.8l-2.1 2.1M5.5 17h3M23.5 17h3" stroke="#0D365F" stroke-width="1.6" stroke-linecap="round"/><path d="M8 24.5h16" stroke="#1F7A8C" stroke-width="1.8" stroke-linecap="round"/></svg>The Good Day Club</span>
  <h2>More good years at home, on their own terms.</h2>
  <p class="lede">The Good Day Club is how we do companion care. We're here before hands-on care is needed, to help your loved one stay independent longer by keeping them moving, eating well, on track with medications, connected and enjoying their days.</p>
  <div class="grid grid-3" style="margin-top:28px">
    <div class="card">{icon("i-strength")}<h3>Keep moving</h3><p>A guided seated exercise routine at every visit, for strength, balance and energy.</p></div>
    <div class="card">{icon("i-heart-honey")}<h3>Joy and activity</h3><p>Conversation, hobbies, music, games and getting out of the house. Days with something to look forward to. <a href="outings.html">See outing ideas</a></p></div>
    <div class="card">{icon("i-bowl")}<h3>Eat well</h3><p>Good meals cooked at home and shared, following any diet their doctor has given them.</p></div>
    <div class="card">{icon("i-clock")}<h3>Medications on time</h3><p>A reminder at the right time, every visit, so nothing gets skipped.</p></div>
    <div class="card">{icon("i-tv")}<h3>Stay connected</h3><p>HomeTogether TV puts family video calls on their TV, with camera-free safety sensors that respect their privacy and independence. <a href="https://tryhometogether.com/">Learn more</a></p></div>
    <div class="card">{icon("i-calendar")}<h3>Start small</h3><p>Join with one or two visits a week and add more only if it helps.</p></div>
  </div>
</div></section>

<section class="section tight"><div class="shell">
  <div class="peek">
    <div class="peek-phone" aria-hidden="true"><div class="peek-screen">
      <span class="peek-k">The Good Day Club</span><b>Tue, 8am to 12pm</b>
      <span class="peek-row">Seated exercise</span><span class="peek-row">Cook lunch together</span><span class="peek-row">Medication reminder</span>
      <span class="peek-btn">Book this visit</span></div></div>
    <div>
      <p class="kicker">Sneak peek</p>
      <h2>Booking a visit will take about a minute.</h2>
      <p class="lede">Our app lets you pick a day, choose what your loved one would like to do, and book. Try it now with sample information.</p>
      <div class="btn-row"><button type="button" class="btn" data-app-preview>See how booking works</button><a class="btn btn-outline" href="join.html">Join the opening list</a></div>
    </div>
  </div>
</div></section>

<section class="section pale edge"><div class="shell">
  <p class="kicker">Built for the workday</p>
  <h2>We do one thing, in the hours families need it most.</h2>
  <p class="lede">Most home care companies spread themselves across nights, weekends and hands-on care. We chose to be the weekday companion, and to do it well.</p>
  <div class="day-bar" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
  <div class="day-bar-labels" aria-hidden="true"><span>8am</span><span>Lunch</span><span>6pm</span></div>
  <div class="grid grid-4" style="margin-top:26px">
    <div class="card">{icon("i-calendar")}<h3>Your workday, covered</h3><p>8 to 6 spans a full workday and the drive there and back. Book a few days a week or all five.</p></div>
    <div class="card">{icon("i-phone")}<h3>A real person, during every visit</h3><p>Every visit happens while our Mustang office is open. If anything comes up, someone who knows your family picks up right then.</p></div>
    <div class="card">{icon("i-handshake")}<h3>Caregivers who chose daytime</h3><p>No night shifts and no weekend rotations means a team of people who want steady daytime work. That's how we plan for a familiar face, week after week.</p></div>
    <div class="card">{icon("i-money")}<h3>One rate, every visit</h3><p>No surcharges and no add-ons. Every service on our list is included in the same hourly rate.</p></div>
  </div>
  <div class="edge-note"><p><b>Thinking about adult day care?</b> This is the at-home version: their own kitchen, their own chair, no van ride to a new building, and one person who is there just for them.</p></div>
</div></section>

<section class="section alt"><div class="shell">
  <p class="kicker">What a visit can look like</p>
  <h2>Help with the everyday, and good company while it's done.</h2>
  <p class="lede">Every visit is planned around the person: their routines, the things they enjoy, and the jobs that have gotten harder.</p>
  <div class="grid grid-3" style="margin-top:28px">{cards}</div>
  <p style="margin-top:22px"><a href="services.html">See everything we help with, including respite for family</a></p>
</div></section>

<section class="section"><div class="shell">
  <p class="kicker">Honest from the first call</p>
  <h2>Companion care, not personal care.</h2>
  <p class="lede">Our Oklahoma license is for companion services, so it's important you know exactly what that covers before you call.</p>
  <div class="boundary" style="margin-top:26px">
    <div><h3>What our caregivers do</h3><ul class="checks">{"".join(f"<li>{t}</li>" for _, t, _ in SERVICES)}</ul></div>
    <div><h3>What they don't do</h3><ul class="nots">{"".join(f"<li>{t}</li>" for t in NOT_DONE)}</ul>
      <p>If your loved one needs hands-on help, we'll tell you so at the first visit rather than take on care we can't give.</p></div>
  </div>
</div></section>

<section class="section pale"><div class="shell">
  <p class="kicker">Getting started</p>
  <h2>Four steps from first call to first visit.</h2>
  <ol class="steps" style="margin-top:26px">
    <li><h3>Call or book online</h3><p>Tell us what's going on. We'll ask a few questions and find a time to come out. Visits begin when we open in {CONFIG['OPENING']}.</p></li>
    <li><h3>Free visit at home</h3><p>We meet your loved one, see the home, and learn their routines and what matters to them.</p></li>
    <li><h3>A written plan</h3><p>Together we write down the help, the days and the hours. We review it with you at least every six months.</p></li>
    <li><h3>Care begins</h3><p>Your caregiver arrives knowing the plan. You can call the office any weekday with questions or changes.</p></li>
  </ol>
  <p style="margin-top:22px"><a href="getting-started.html">More about getting started</a></p>
</div></section>

<section class="section tight"><div class="shell">
  <div class="grid grid-2" style="align-items:center">
    <div>
      <p class="kicker">Service area</p>
      <h2>Where we go</h2>
      <p>Our office is in Mustang, and our caregivers serve families close by.</p>
      <p><a href="service-area.html">See our service area</a></p>
    </div>
    <ul class="towns">{"".join(f"<li>{t}</li>" for t in TOWNS)}</ul>
  </div>
</div></section>

<section class="section dark"><div class="shell center">
  <p class="kicker">Our promise</p>
  <p class="promise">"We will care for your loved one with the same respect, kindness, and dignity we would want for our own family."</p>
  <p>Family owned, never a franchise. Caring for families since 2017.</p>
</div></section>

{cta_band()}'''

def page_services():
    blocks = "\n".join(
        f'<div class="card">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in SERVICES)
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Services</p>
  <h1>What our companion caregivers do.</h1>
  <p class="lede">Companion care is for older adults who can still take care of themselves physically but need company, a hand around the house, or a ride. Here's everything a visit can include.</p>
  <p>Every visit is part of <a href="index.html#good-day-club">The Good Day Club</a>, our way of helping older adults stay independent longer.</p>
</div></section>

<section class="section"><div class="shell">
  <div class="grid grid-3">{blocks}</div>
  <div style="margin-top:22px">{HT_CARD}</div>
{GUIDE_SERVICES_LINE if CONFIG["GUIDE"] else ""}
</div></section>

<section class="section alt"><div class="shell">
  <div class="grid grid-2" style="align-items:start">
    <div>
      <p class="kicker">Good to know</p>
      <h2>What companion care doesn't include.</h2>
      <p>Our license from the Oklahoma State Department of Health is for companion services. That means our caregivers don't give hands-on help with the body. They will not help with:</p>
      <ul class="nots">{"".join(f"<li>{t}</li>" for t in NOT_DONE)}</ul>
      <p>If those needs come up, we'll tell you honestly and talk with you about what kind of care would fit.</p>
    </div>
    <div class="card">
      <h3>Weekdays are what we do</h3>
      <dl class="hours"><dt>Days</dt><dd>Monday to Friday</dd><dt>Hours</dt><dd>8am to 6pm</dd></dl>
      <p>We focus on the workday, the hours when family is at work and the house is quietest. Visits fit the days that suit your loved one, and our office is open the whole time a caregiver is with them.</p>
      <p>We don't cover evenings, overnights or weekends.</p>
      <p>After hours, you can still reach us at {v("AFTER_HOURS_PHONE", "after-hours phone")}.</p>
    </div>
  </div>
</div></section>

{cta_band()}'''

def page_pricing():
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Pricing</p>
  <h1>One hourly rate. No surprises.</h1>
  <p class="lede">Companion care is paid privately by the hour. Every service on our list is included in the same rate, with no surcharges and no add-ons.</p>
</div></section>

<section class="section"><div class="shell grid grid-2" style="align-items:start">
  <div class="price-card">
    <p class="kicker">Companion care</p>
    <div class="price">{v("RATE", "$__")}<small> per hour</small></div>
    <p style="color:var(--muted)">Monday to Friday, 8am to 6pm. Every visit is part of <a href="index.html#good-day-club">The Good Day Club</a>.</p>
    <ul class="checks">
      <li>Companionship, light housekeeping and meals</li>
      <li>Errands, shopping and rides to appointments</li>
      <li>Seated exercise and medication reminders</li>
      <li>Respite for family caregivers</li>
      <li>A written plan, reviewed at least every six months</li>
    </ul>
    <p><b>Minimums:</b> {v("MIN_VISIT", "__ hours")} per visit and {v("MIN_WEEK", "__ hours")} per week, so you can start with one visit a week.</p>
    <a class="btn" href="join.html">Join the opening list</a>
  </div>
  <div>
    <div style="margin-bottom:28px">{HT_CARD}</div>
    <h2>Common questions about cost</h2>
    <h3>Is the first visit free?</h3>
    <p>Yes. We come to the home, meet your loved one and talk through what would help. There's no cost and no obligation.</p>
    <h3>Will Medicare or Medicaid pay for this?</h3>
    {GUIDE_PRICING_LINE if CONFIG["GUIDE"] else "<p>Companion care is paid privately. We don't bill Medicare or Medicaid.</p>"}
    <h3>What about long-term care insurance?</h3>
    <p>Some policies pay toward companion care and some don't. Check with the insurance company about what the policy covers before care starts.</p>
    <h3>Are your caregivers your employees?</h3>
    <p>Yes. We handle their pay, taxes and insurance, so you never have to.</p>
  </div>
</div></section>

{cta_band()}'''

def page_getting_started():
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Getting started</p>
  <h1>From the first call to the first visit.</h1>
  <p class="lede">Most families call when they've started to worry. Here's what happens next, so you know what to expect.</p>
</div></section>

<section class="section"><div class="shell">
  <ol class="steps vertical">
    <li><h3>You call or book a visit</h3><p>Tell us about your loved one and what's been hard lately. We'll answer your questions, including cost, and set a time to come out. Call {v("PHONE", "(405) phone")} Monday to Friday, 8 to 6, or <a href="join.html">join our opening list</a>. Visits begin in {CONFIG['OPENING']}.</p></li>
    <li><h3>We visit at home, free</h3><p>We sit down with your loved one, and with you if you'd like to be there. We learn their routines, what they enjoy, what they'd like help with, and what worries the family. If they need more than companion care, we'll tell you.</p></li>
    <li><h3>We write a service plan together</h3><p>The plan lists the help they'll get, the days and the hours. It's written with your loved one and the family, shared with the caregiver before the first visit, and reviewed with you at least every six months, or sooner if things change.</p></li>
    <li><h3>We match a caregiver</h3><p>Every caregiver has passed a fingerprint background check through Oklahoma's OKSCREEN program. We look for someone whose personality and interests fit your loved one.</p></li>
    <li><h3>Care begins, and we stay close</h3><p>Our office is in Mustang and our caregivers are supervised from there. If anything needs to change, call us any weekday and we'll update the plan.</p></li>
  </ol>
</div></section>

{cta_band()}'''

TOWNS = ["Mustang", "Yukon", "Tuttle", "El Reno", "Piedmont", "Bethany", "Nichols Hills",
         "West Oklahoma City", "Southwest Oklahoma City", "Northwest Oklahoma City"]

# ZIP -> (area, counties). Counties from the Census 2020 ZCTA-to-county file.
ZIPS = [
    ("73064", "Mustang", "Canadian"), ("73099", "Yukon", "Canadian"), ("73089", "Tuttle", "Grady"),
    ("73036", "El Reno", "Canadian"), ("73078", "Piedmont", "Canadian"), ("73008", "Bethany", "Oklahoma"),
    ("73116", "Nichols Hills", "Oklahoma"),
    ("73127", "West Oklahoma City", "Oklahoma, Canadian"), ("73128", "West Oklahoma City", "Oklahoma, Canadian"),
    ("73169", "West Oklahoma City", "Oklahoma, Cleveland"), ("73179", "Southwest Oklahoma City", "Oklahoma, Canadian"),
    ("73159", "Southwest Oklahoma City", "Oklahoma, Cleveland"), ("73170", "Southwest Oklahoma City", "Cleveland"),
    ("73173", "Southwest Oklahoma City", "Cleveland"), ("73132", "Northwest Oklahoma City", "Oklahoma"),
    ("73162", "Northwest Oklahoma City", "Oklahoma"), ("73142", "Northwest Oklahoma City", "Oklahoma"),
]

def page_service_area():
    slugs = {"Mustang": "mustang", "Yukon": "yukon", "Tuttle": "tuttle", "El Reno": "el-reno", "Piedmont": "piedmont", "Bethany": "bethany",
             "Nichols Hills": "nichols-hills", "West Oklahoma City": "oklahoma-city", "Southwest Oklahoma City": "oklahoma-city", "Northwest Oklahoma City": "oklahoma-city"}
    towns = "".join(f'<li><a href="companion-care-{slugs[t]}-ok.html">{t}</a></li>' if t in slugs else f"<li>{t}</li>" for t in TOWNS)
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Service area</p>
  <h1>Companion care in Mustang and nearby towns.</h1>
  <p class="lede">Our office is in Mustang, and our caregivers serve families close by so they're never far away. Check your ZIP code or explore the map.</p>
</div></section>

<section class="section sa-section"><div class="shell">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" integrity="sha512-h9FcoyWjHcOcmEVkxOfTLnmZFWIH0iZhZT1H2TbOq55xssQGEJHEaIm+PgoUaZbRvQTNTluNOEfb1ZRy6D3BOw==" crossorigin="anonymous" referrerpolicy="no-referrer">
  <div class="sa-wrap">
    <div class="sa-map-box">
      <div id="sa-map" class="sa-map" role="region" aria-label="Map of the ZIP codes and counties we serve around Mustang, Oklahoma"></div>
      <p class="sa-map-fallback">The map couldn't load. Every ZIP code we serve is listed below.</p>
    </div>
    <aside class="sa-panel">
      <h2>Is your home in our area?</h2>
      <form id="sa-check" class="sa-check" novalidate>
        <label for="sa-zip" class="sr-only">Your ZIP code</label>
        <input id="sa-zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="Enter your ZIP code">
        <button class="btn" type="submit">Check</button>
      </form>
      <p id="sa-result" class="sa-result" role="status" aria-live="polite"></p>

      <h3>Drive time from our Mustang office</h3>
      <ul class="sa-legend">
        <li><span style="background:#0F5563"></span>15 minutes or less</li>
        <li><span style="background:#3E98A8"></span>16 to 25 minutes</li>
        <li><span style="background:#A9DDD5"></span>More than 25 minutes</li>
      </ul>

      <h3>Counties we serve</h3>
      <div class="sa-counties">
        <button type="button" data-county="all" aria-pressed="true">Whole area</button>
        <button type="button" data-county="Canadian County">Canadian</button>
        <button type="button" data-county="Oklahoma County">Oklahoma</button>
        <button type="button" data-county="Cleveland County">Cleveland</button>
        <button type="button" data-county="Grady County">Grady</button>
      </div>
      <p class="sa-note">We serve parts of each county, the ZIP codes shaded on the map. Tap any of them for details.</p>
    </aside>
  </div>
  <script>window.SA_ZIP_COUNTIES = {json.dumps({z: c for z, _, c in ZIPS})};</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" integrity="sha512-puJW3E/qXDqYp9IfhAI54BJEaWIfloJ7JWs7OeD5i6ruC9JZL1gERT1wjtwXFlh7CjE7ZJ+/vcRZRkIYIb6p4g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script src="assets/service-map.js"></script>
</div></section>

<section class="section alt"><div class="shell grid grid-2" style="align-items:start">
  <div>
    <h2>Where we go</h2>
    <ul class="towns">{towns}</ul>
    <p>Parts of Canadian, Cleveland, Grady and Oklahoma counties. Not sure whether you're in our area? Call {v("PHONE", "(405) phone")} and we'll tell you right away.</p>
  </div>
  <div class="card">
    <h3>Our office</h3>
    <p>{addr()}</p>
    <dl class="hours"><dt>Office hours</dt><dd>Monday to Friday, 8am to 6pm</dd><dt>After hours</dt><dd>{v("AFTER_HOURS_PHONE", "after-hours phone")}</dd></dl>
    <p style="margin:0">Looking for care in Missouri? Visit <a href="https://mo-care.com/">mo-care.com</a>.</p>
  </div>
</div></section>

<section class="section"><div class="shell">
  <h2>ZIP codes we serve</h2>
  <ul class="zips">{"".join(f"<li><b>{z}</b> {a}</li>" for z, a, _ in ZIPS)}</ul>
</div></section>

{cta_band()}'''

def page_about():
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">About us</p>
  <h1>A family company, now in Mustang.</h1>
  <p class="lede">We help seniors keep living safely, comfortably, and with dignity in the place that means the most to them, home. We've been doing it one family at a time since 2017.</p>
</div></section>

<section class="section"><div class="shell" style="max-width:900px">
  <ol class="story">
    <li><p class="yr">2017 &middot; Where it began</p><h2>A family decides home shouldn't be negotiable.</h2>
      <p>Caring Companions started in Springfield, Missouri. We had watched too many people moved into facilities before they were ready, not because they couldn't live at home, but because they didn't have the right support.</p></li>
    <li><p class="yr">The years since &middot; Earning trust</p><h2>Growing the way trust grows: one family telling another.</h2>
      <p>Word spread from family to family. We kept the rules that made us different: caregivers are our own employees, never contractors, and every plan is built around the person's routines, preferences and story.</p></li>
    <li><p class="yr">{CONFIG["OPENING"]} &middot; Mustang</p><h2>Companion care, built around the workday.</h2>
      <p>Our Oklahoma office brings that same approach to Mustang and the towns around it, starting with what so many working families ask for first: a dependable, friendly companion during the day, and <a href="index.html#good-day-club">The Good Day Club</a> to help their loved one stay independent longer.</p></li>
  </ol>
</div></section>

<section class="section alt"><div class="shell">
  <p class="kicker">What we stand for</p>
  <h2>Four things that don't change.</h2>
  <div class="grid grid-4" style="margin-top:24px">
    <div class="card">{icon("i-family")}<h3>Family owned</h3><p>We're not a franchise. Caring Companions is family owned, and our compassion and quality of care run higher because of that personal touch.</p></div>
    <div class="card">{icon("i-handshake")}<h3>Our own employees</h3><p>Every caregiver is screened and employed by us, never a contractor. We handle the taxes, insurance and backup support.</p></div>
    <div class="card">{icon("i-sun")}<h3>Here for the workday</h3><p>Monday to Friday, 8am to 6pm, with our Mustang office open the whole time a caregiver is with your loved one.</p></div>
    <div class="card">{icon("i-sprout")}<h3>Always improving</h3><p>We're forward-thinking and always getting better, because our mission is to make life better for seniors and the families who love them.</p></div>
  </div>
</div></section>

<section class="section"><div class="shell grid grid-2" style="align-items:start">
  <div>
    <p class="kicker">Our caregivers</p>
    <h2>More than a job. A calling.</h2>
    <p>Our caregivers come from all walks of life, united by one mission: to help older adults live with dignity, comfort and joy at home. We look for compassion, kindness and patience, and we follow Oklahoma's licensing requirements for companion services, including a fingerprint background check for every caregiver.</p>
    <p><a href="careers.html">We're hiring in Mustang</a></p>
  </div>
  <div class="card">
    <h3>How we match</h3>
    <ul class="checks">
      <li>Matched by personality, experience and what your loved one enjoys</li>
      <li>Your caregiver knows the service plan before the first visit</li>
      <li>Preferences and routines honored from day one</li>
      <li>Focused on meaningful connection, not just tasks</li>
      <li>We keep checking the fit. If it isn't working, tell us and we'll match someone else.</li>
    </ul>
  </div>
</div></section>

<section class="section pale"><div class="shell" style="max-width:900px">
  <p class="kicker">How we work with families</p>
  <h2>Honest, even when the answer isn't us.</h2>
  <p class="lede">We believe families deserve clear information before making a hard decision. We publish our rate so you don't have to call five agencies for a ballpark, and we'll always point you toward the care that's right for your situation, even when it isn't ours.</p>
  <p>Most families start smaller than they expect and adjust after the first few weeks. Needs change, and a plan written in March may be wrong by August. Yours is meant to be rewritten when that happens.</p>
</div></section>

<section class="section dark"><div class="shell center">
  <p class="kicker">Our promise</p>
  <p class="promise">"We will care for your loved one with the same respect, kindness, and dignity we would want for our own family."</p>
  <p>Home isn't just where someone lives. It's where memories, comfort and identity live. We're honored to help our clients stay there, for as long as possible.</p>
</div></section>

<section class="section"><div class="shell">
  <p class="kicker">One company, care wherever home is</p>
  <h2>Part of the Caring Companions family.</h2>
  <div class="grid grid-2" style="margin-top:22px">
    <a class="card card-link" href="https://mo-care.com/"><h3>Caring Companions Missouri</h3><p>In-home care across Southwest Missouri, where it all started in 2017.</p></a>
    <a class="card card-link" href="https://tryhometogether.com/"><h3>HomeTogether TV</h3><p>Family video calls and camera-free safety sensors on your loved one's TV, anywhere in the country.</p></a>
  </div>
</div></section>

{cta_band()}'''

def apply_form():
    return '''<form class="form card join-form" data-join novalidate>
  <input type="radio" name="kind" value="caregiver" checked hidden>
  <label>Your name<input name="name" autocomplete="name" required maxlength="120"></label>
  <div class="join-row"><label>Phone<input name="phone" type="tel" autocomplete="tel" maxlength="40"></label>
  <label>Email<input name="email" type="email" autocomplete="email" maxlength="200"></label></div>
  <label>Your ZIP code<input name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5"></label>
  <label>Caregiving experience<select name="experience"><option value="">Choose one</option><option>None yet, but I'd love to learn</option><option>Less than 1 year</option><option>1 to 3 years</option><option>More than 3 years</option></select></label>
  <fieldset class="join-ints"><legend>A little more about you</legend>
    <label><input type="checkbox" name="interests" value="weekdays-all"> I can work most weekdays, 8am to 6pm</label>
    <label><input type="checkbox" name="interests" value="weekdays-some"> I can work some weekdays</label>
    <label><input type="checkbox" name="interests" value="drives"> I have a driver's license, a car and auto insurance</label>
    <label><input type="checkbox" name="interests" value="cna-or-hha"> I have a CNA, HHA or similar certificate</label>
  </fieldset>
  <label>When could you start?<select name="timing"><option value="">Choose one</option><option>Early 2027</option><option>Spring 2027</option><option>When you open in June 2027</option></select></label>
  <label>Why would you like to be a companion caregiver? <span class="og-opt">(optional)</span><textarea name="message" maxlength="2000"></textarea></label>
  <label class="join-consent"><input type="checkbox" name="may_contact" checked> It's OK to contact me about working with Caring Companions Oklahoma.</label>
  <label class="hp-field" aria-hidden="true">Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label>
  <button class="btn" type="submit">Send my application</button>
  <p class="join-status" role="status" aria-live="polite"></p>
  <p class="form-note">We only use your details to contact you about working with us. We never sell or share them.</p>
</form>'''

def job_schema():
    job = {
        "@context": "https://schema.org", "@type": "JobPosting",
        "title": "Companion Caregiver",
        "description": "<p>Caring Companions Oklahoma is hiring companion caregivers in Mustang, Oklahoma ahead of our June 2027 opening. Spend weekday daytime hours with older adults: conversation, games and walks, light housekeeping, meal preparation, errands, rides to appointments, a simple seated exercise routine and medication reminders. No nights, no weekends, and no hands-on personal care. Every caregiver passes a fingerprint background check through Oklahoma's OKSCREEN program.</p>",
        "datePosted": "2026-10-16", "validThrough": "2027-06-30T23:59",
        "hiringOrganization": {"@type": "Organization", "name": "Caring Companions Oklahoma", "sameAs": CONFIG["DOMAIN"], "logo": CONFIG["DOMAIN"] + "/assets/cc-logo.png"},
        "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": "Mustang", "addressRegion": "OK", "postalCode": "73064", "addressCountry": "US"}},
        "directApply": True,
    }
    return '<script type="application/ld+json">' + json.dumps(job) + '</script>'

def page_careers():
    return f'''{job_schema()}
<section class="page-hero"><div class="shell">
  <p class="kicker">Careers <span class="open-chip">Now hiring</span></p>
  <h1>Now hiring companion caregivers in Mustang.</h1>
  <p class="lede">We're licensed and building our Mustang team ahead of our {CONFIG["OPENING"]} opening. Daytime weekday hours, no nights, no weekends, and work that matters: keeping someone company and helping them stay at home.</p>
  <div class="btn-row" style="margin-top:18px"><a class="btn" href="#apply">Apply now</a><a class="btn btn-outline" href="{phone_href()}">Call {v("PHONE", "(405) phone")}</a></div>
</div></section>

<section class="section"><div class="shell">
  <div class="grid grid-3">
    <div class="card">{icon("i-sun")}<h3>Daytime, weekdays</h3><p>Monday to Friday, between 8am and 6pm. Evenings and weekends are yours.</p></div>
    <div class="card">{icon("i-heart-honey")}<h3>Work that matters</h3><p>You're the reason someone's week has something to look forward to.</p></div>
    <div class="card">{icon("i-handshake")}<h3>A local team</h3><p>You're supervised from our Mustang office, with people who know you by name.</p></div>
  </div>
</div></section>

<section class="section alt" id="apply"><div class="shell grid grid-2" style="align-items:start">
  <div>
    <h2>The job</h2>
    <ul class="checks">
      <li>Spending time with older adults: conversation, games, walks and hobbies</li>
      <li>Light housekeeping, laundry and meal preparation</li>
      <li>Errands, shopping and driving clients to appointments</li>
      <li>Leading a simple seated exercise routine</li>
      <li>Friendly medication reminders</li>
      <li>Giving family caregivers a break</li>
    </ul>
    <p>This is companion work. You won't be asked to give hands-on personal care.</p>
    <h3>What you'll need</h3>
    <ul class="checks">
      <li>A kind, patient, dependable way with people</li>
      <li>To pass a fingerprint background check through Oklahoma's OKSCREEN program</li>
      <li>A valid driver's license and auto insurance, if you'll drive clients</li>
    </ul>
    <h3>What happens next</h3>
    <p>We read every application. If it looks like a fit, we'll call you to set up an interview in Mustang.</p>
  </div>
  <div>
    <h2>Apply now</h2>
    <p>It takes about two minutes. No resume needed.</p>
    {apply_form()}
  </div>
</div></section>
'''

def page_contact():
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Contact</p>
  <h1>Talk to us.</h1>
  <p class="lede">We open in Mustang in {CONFIG["OPENING"]}. Add your name to the opening list, or reach us any weekday.</p>
</div></section>

<section class="section"><div class="shell grid grid-2" style="align-items:start">
  {join_form()}
  <div>
    <div class="card" style="margin-bottom:18px">
      <h3>Call us</h3>
      <p><a class="btn" href="{phone_href()}">{icon("i-phone", "")} {v("PHONE", "(405) phone")}</a></p>
      <dl class="hours"><dt>Office hours</dt><dd>Monday to Friday, 8am to 6pm</dd><dt>After hours</dt><dd>{v("AFTER_HOURS_PHONE", "after-hours phone")}</dd>{email_dd()}</dl>
    </div>
    <div class="card">
      <h3>Visit our office</h3>
      <p style="margin:0">{addr()}</p>
    </div>
  </div>
</div></section>
'''

def join_form(kind="family"):
    def k(v, label, sub):
        chk = " checked" if v == kind else ""
        return f'<label class="join-kind"><input type="radio" name="kind" value="{v}"{chk}><span><b>{label}</b><small>{sub}</small></span></label>'
    towns = "".join(f"<option>{t}</option>" for t in TOWNS) + "<option>Somewhere else</option>"
    return f'''<form class="form card join-form" data-join novalidate>
  <fieldset class="join-kinds"><legend>I'm interested as</legend>
    {k("family", "A family", "Care for someone I love")}
    {k("caregiver", "A caregiver", "Join the Mustang team")}
    {k("partner", "A partner", "I refer families")}
  </fieldset>
  <label>Your name<input name="name" autocomplete="name" required maxlength="120"></label>
  <div class="join-row"><label>Email<input name="email" type="email" autocomplete="email" maxlength="200"></label>
  <label>Phone<input name="phone" type="tel" autocomplete="tel" maxlength="40"></label></div>
  <label>ZIP code<input name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5"></label>
  <div data-for="family">
    <label>Who is it for?<select name="for_whom"><option value="">Choose one</option><option>My mother</option><option>My father</option><option>Both parents</option><option>My spouse</option><option>Myself</option><option>Someone else</option></select></label>
    <fieldset class="join-ints"><legend>What interests you?</legend>
      <label><input type="checkbox" name="interests" value="good-day-club"> Good Day Club visits</label>
      <label><input type="checkbox" name="interests" value="outings"> Outings</label>
      <label><input type="checkbox" name="interests" value="respite"> A break for the family</label>
      <label><input type="checkbox" name="interests" value="hometogether-tv"> HomeTogether TV</label>
{GUIDE_CHECKBOX if CONFIG["GUIDE"] else ""}    </fieldset>
    <label>When might you need help?<select name="timing"><option value="">Choose one</option><option>As soon as you open</option><option>Later in 2027</option><option>Just planning ahead</option></select></label>
  </div>
  <div data-for="caregiver">
    <label>Caregiving experience<select name="experience"><option value="">Choose one</option><option>None yet, but I'd love to learn</option><option>Less than 1 year</option><option>1 to 3 years</option><option>More than 3 years</option></select></label>
    <label>When could you start?<select name="timing"><option value="">Choose one</option><option>Early 2027</option><option>Spring 2027</option><option>When you open</option></select></label>
  </div>
  <label>Anything you'd like us to know? <span class="og-opt">(optional)</span><textarea name="message" maxlength="2000"></textarea></label>
  <label class="join-consent"><input type="checkbox" name="may_contact" checked> It's OK to contact me about Caring Companions Oklahoma.</label>
  <label class="hp-field" aria-hidden="true">Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label>
  <button class="btn" type="submit">Add me to the list</button>
  <p class="join-status" role="status" aria-live="polite"></p>
  <p class="form-note">We only use your details to contact you about Caring Companions. We never sell or share them.</p>
</form>'''

def page_join():
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Opening {CONFIG["OPENING"]}</p>
  <h1>Join the opening list.</h1>
  <p class="lede">We're licensed and getting ready to open in Mustang. Families, future caregivers and referral partners: add your name and we'll be in touch as opening gets closer.</p>
</div></section>

<section class="section"><div class="shell grid grid-2" style="align-items:start">
  {join_form()}
  <div>
    <div class="card app-teaser">
      <p class="kicker">Sneak peek</p>
      <h3>Booking a visit will take about a minute.</h3>
      <p>Pick a day, choose what they'd like to do, and you're set. Try it now with sample information.</p>
      <button type="button" class="btn" data-app-preview>See how booking works</button>
    </div>
    <div class="card" style="margin-top:18px">
      <h3>What happens next</h3>
      <ul class="checks">
        <li>Your name goes on our list. Nothing is booked and there's nothing to pay.</li>
        <li>As opening gets closer, we'll reach out to the people who said it's OK.</li>
        <li>Caregivers: we'll invite you to apply when hiring for Mustang begins.</li>
      </ul>
    </div>
  </div>
</div></section>'''

MO = "https://mo-care.com"
RESOURCES = [
    ("Free course", "i-grad", [
        ("/dementia-journey/", "The Dementia Journey", "Nine short modules for families caring for someone with dementia: what's changing in the brain, how to stop arguing, calmer days, and caring for yourself too."),
    ]),
    ("Planning tools", "i-clipboard", [
        ("/family-checklist", "Family checklist", "Signs it may be time for help, and what to get in order before you need it."),
        ("/family-meeting-planner", "Family meeting planner", "Get everyone on the same page about who does what."),
        ("/home-safety-check", "Home safety check", "Walk through the house room by room and spot the easy fixes."),
        ("/decision-journal", "Decision journal", "Write down what you're noticing so the big decisions get easier."),
        ("/compare-care", "Compare care options", "Home care, adult day, assisted living and more, side by side."),
    ]),
    ("Guides for families", "i-book", [
        ("/guides/dementia-and-alzheimers", "Recognizing early signs of dementia", ""),
        ("/guides/best-practices-for-dementia-care", "Best practices for dementia care", ""),
        ("/guides/caregiver-burnout", "Caregiver burnout: what helps", ""),
        ("/guides/fall-prevention-at-home", "Fall prevention at home", ""),
        ("/guides/home-safety-room-by-room", "Home safety room by room", ""),
        ("/guides/eating-well-as-we-age", "Eating well as we age", ""),
        ("/guides/medication-management", "Medication management made simple", ""),
        ("/guides/hospital-discharge", "Coming home after a hospital stay", ""),
        ("/guides/stroke-recovery-at-home", "Stroke recovery at home", ""),
        ("/guides/parkinsons-disease-at-home", "Parkinson's disease at home", ""),
        ("/guides/diabetes-care-for-seniors", "Diabetes care for seniors", ""),
        ("/guides/living-well-with-heart-failure", "Living well with heart failure", ""),
        ("/guides/managing-copd-at-home", "Managing COPD at home", ""),
        ("/guides/planning-for-end-of-life-care", "Planning for end-of-life care", ""),
    ]),
]

def page_resources():
    blocks = []
    for heading, ic, items in RESOURCES:
        if heading == "Guides for families":
            links = "".join(f'<li><a href="{MO}{path}">{title}</a></li>' for path, title, _ in items)
            blocks.append(f'<section class="section tight"><div class="shell"><h2>{icon(ic, "icon")} {heading}</h2><ul class="guide-list">{links}</ul></div></section>')
        else:
            cards = "".join(f'<a class="card card-link" href="{MO}{path}"><h3>{title}</h3><p>{desc}</p></a>' for path, title, desc in items)
            cols = "grid-3" if len(items) > 1 else "grid-2"
            blocks.append(f'<section class="section tight"><div class="shell"><h2>{icon(ic, "icon")} {heading}</h2><div class="grid {cols}">{cards}</div></div></section>')
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Family resources</p>
  <h1>Free help for the family, too.</h1>
  <p class="lede">Caring for a parent is a lot, especially around a job. These free courses, tools and guides are for you, whether or not you ever use our services.</p>
  <p class="form-note" style="margin-top:12px">They live on our main Caring Companions site, mo-care.com, so they open there.</p>
</div></section>
{"".join(blocks)}
<section class="section tight"><div class="shell">
  <div class="card" style="max-width:860px">
    <h3>Staying close from a distance</h3>
    <p>HomeTogether TV, from the Caring Companions family, puts video calls and gentle check-ins right on your loved one's TV. It works anywhere in the country.</p>
    <a href="https://tryhometogether.com/">Learn about HomeTogether TV</a>
  </div>
</div></section>

{cta_band()}'''

GUIDE_FAQ = [
    ("Does every family get the respite visits?",
     "No, and we'd rather say so plainly. Everyone accepted into GUIDE gets the care navigator and the 24/7 line. Respite goes to families where the dementia has progressed to a certain stage and the caregiver is carrying a heavy load, which Medicare measures with two standard assessments: one that stages the dementia and one that asks the caregiver how they're holding up. If your loved one is early in the disease, they may be enrolled without respite at first and qualify later as things change."),
    ("Is this really free?",
     "The GUIDE services are covered by Medicare, so there's no bill to you for them. What it isn't is unlimited care. Medicare sets a yearly respite budget, and how many visits it buys depends on Medicare's rate for your area. If you need more care than that, the rest is regular companion care at our hourly rate, and we'll tell you exactly what it costs before you commit to anything."),
    ("Does this replace their doctor?",
     "No. Nothing changes about their doctor, neurologist or anyone else on their team. GUIDE adds a care navigator and a support line alongside them."),
    ("Mom has a Medicare Advantage plan. Can we switch?",
     "Medicare Advantage plans aren't eligible for GUIDE, and we wouldn't tell you to change plans over it. Switching back to Original Medicare affects the rest of her coverage, and that's a decision to make with a licensed Medicare counselor, not a home care company. Call us anyway; there may be other ways we can help."),
    ("Dad is in assisted living or memory care. Does he qualify?",
     "Not anymore, and we're sorry to be the ones to say it. Medicare changed the rules in 2026 to limit GUIDE to people living in a private home or in independent living. Assisted living, memory care, group homes and board and care homes are no longer eligible. If he's already enrolled, don't ask to be unenrolled; his medical group handles that."),
    ("She lives in a retirement community. Is that independent living or assisted living?",
     "What matters is what her lease pays for, not what the building calls itself. If she has her own apartment and the community doesn't provide personal care, medication management or supervision as part of her agreement, that's independent living and she can qualify. If any of that care is included in what she pays, she can't. Give us the community name and we'll help you work it out."),
    ("How long does it take?",
     "Plan on a few weeks from the assessment to approval. That's exactly why we'd rather start companion visits now, as regular private-pay care, than have you sitting at home waiting on a form."),
    ("What's the catch?",
     "GUIDE covers a set amount, and people sometimes leave the program without much warning, usually because they start hospice, move to a nursing home or switch to a Medicare Advantage plan. Visits after that date aren't covered. So we ask every family to sign a service agreement saying anything Medicare doesn't cover is billable to them. We're not trying to catch anyone out; we're making sure nobody opens a surprise bill."),
    ("Do we have to use Caring Companions?",
     "No. You can be enrolled in GUIDE and use a different respite provider, or adult day services instead. We'd like to be the ones, but the program belongs to you, not to us."),
    ("What if we live outside your area?",
     "We serve Mustang and the towns around it, including west, southwest and northwest Oklahoma City. If you're further out, your loved one may still be eligible for GUIDE through another provider. Call and ask; it costs nothing to find out."),
]

def page_guide():
    faq = "".join(f'<details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in GUIDE_FAQ)
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Medicare GUIDE program</p>
  <h1>Medicare may pay for dementia respite care.</h1>
  <p class="lede">GUIDE is a Medicare program for people living with dementia at home. Every enrolled family gets a dementia care navigator and a 24/7 support line, and families further along in the disease can also get respite visits from our caregivers, billed to Medicare instead of to you.</p>
  <p>Most eligible families never hear it exists.</p>
  <div class="btn-row" style="margin-top:18px">
    <a class="btn" href="{phone_href()}">{icon("i-phone", "")} Call {v("PHONE", "(405) phone")} to check eligibility</a>
  </div>
  <p class="form-note" style="margin-top:10px">We'll go through the questions with you in about five minutes.</p>
</div></section>

<section class="section"><div class="shell">
  <h2>What GUIDE covers</h2>
  <div class="grid grid-3" style="margin-top:22px">
    <div class="card">{icon("i-heart-honey")}<h3>Respite visits</h3><p>Four-hour visits from one of our caregivers so you can rest, work or see your own doctor, billed to Medicare rather than to you. Medicare decides who qualifies based on how far the dementia has progressed and how much strain the caregiver is under.</p></div>
    <div class="card">{icon("i-compass")}<h3>A dementia care navigator</h3><p>A trained person who calls every month. Education, resources, help finding things, and someone to talk to who has seen this before.</p></div>
    <div class="card">{icon("i-phone")}<h3>A 24/7 support line</h3><p>Dementia doesn't keep business hours. Urgent questions, behavior nobody prepared you for, any hour of the night.</p></div>
  </div>
  <div class="grid grid-3 guide-facts" style="margin-top:18px">
    <div><b>4 hours</b><span>per respite visit, scheduled around you</span></div>
    <div><b>Weekdays</b><span>our visits run Monday to Friday, 8am to 6pm</span></div>
    <div><b>July 1</b><span>respite resets every year, and unused visits don't roll over</span></div>
  </div>
  <p class="form-note" style="margin-top:16px">Our caregivers provide companion respite: company, supervision, meals and activities. They don't give hands-on personal care.</p>
</div></section>

<section class="section alt"><div class="shell">
  <h2>What this is actually for</h2>
  <p class="lede">Families caring for someone with dementia at home tend to run out of road. The caregiver gets sick, or exhausted, or has to go back to work, and someone who could have stayed home longer ends up in a facility. GUIDE pays for the three things that usually break first.</p>
  <div class="grid grid-3" style="margin-top:22px">
    <div class="card"><h3>You're worn out</h3><p>Respite isn't a luxury, and it isn't admitting defeat. It's the afternoon you get to go to your own doctor, or a grandchild's game, or just sleep.</p></div>
    <div class="card"><h3>Nobody told you what happens next</h3><p>Most families are handed a diagnosis and sent home. The care navigator tells you what the next stage looks like, which paperwork matters, and which worries are worth your energy.</p></div>
    <div class="card"><h3>It's 2am and they won't settle</h3><p>That's what the 24/7 line is for. Not an answering service that takes a message, but a clinical line that can talk you through it.</p></div>
  </div>
</div></section>

<section class="section"><div class="shell">
  <h2>Who qualifies</h2>
  <p class="lede">Two things decide most of it: the kind of Medicare your loved one has, and where they live. Medicare changed the residence rule in 2026, so if someone told you assisted living was fine, that's no longer true.</p>
  <div class="boundary" style="margin-top:22px">
    <div><h3>Perfectly fine</h3><ul class="checks">
      <li>Original (traditional) Medicare</li>
      <li>A dementia or memory impairment diagnosis</li>
      <li>Living at home, alone or with family</li>
      <li>A house, apartment or condo, including a family member's home</li>
      <li>Independent living, where care isn't part of the lease</li>
      <li>Palliative care (this isn't hospice)</li>
      <li>Having Medicaid or VA benefits as well</li>
    </ul></div>
    <div><h3>Rules it out</h3><ul class="nots">
      <li>A Medicare Advantage plan (any plan name)</li>
      <li>Assisted living, memory care, a group home, or board and care</li>
      <li>Living in a nursing home</li>
      <li>Enrolled in Medicare hospice</li>
      <li>Enrolled in PACE</li>
      <li>Already enrolled in another GUIDE program</li>
    </ul></div>
  </div>
</div></section>

<section class="section pale"><div class="shell">
  <h2>How it goes from here</h2>
  <p class="lede">The honest version, including the part where you wait.</p>
  <ol class="steps" style="margin-top:22px;grid-template-columns:repeat(3,1fr)">
    <li><h3>We talk</h3><p>Free, with no obligation, at home or on the phone. We go through the eligibility questions and answer whatever you want to ask.</p></li>
    <li><h3>The assessment</h3><p>A full assessment is completed with you and your loved one and sent to Medicare. Plan on a few weeks for approval.</p></li>
    <li><h3>Care starts</h3><p>We don't make you wait on paperwork. If you need help now, we can start weekday companion visits as regular care and let the Medicare side catch up.</p></li>
  </ol>
  <div class="edge-note"><p><b>Good to know before you count on it.</b> Respite visits don't roll over. Unused visits expire June 30 and a fresh year starts July 1, so families who save them for a rainy day tend to lose them. We can only bill Medicare once GUIDE enrollment is approved, and how much respite is available follows Medicare's rules, not ours.</p></div>
</div></section>

<section class="section"><div class="shell" style="max-width:860px">
  <h2>Questions families actually ask</h2>
  <div class="faqs">{faq}</div>
</div></section>

<section class="section alt"><div class="shell">
  <div class="grid grid-2" style="align-items:center">
    <div>
      <p class="kicker">If you work with families</p>
      <h2>Your dementia families may be missing a Medicare benefit.</h2>
      <p>Discharge planners, memory clinics, home health, elder law and social workers: most professionals haven't heard of GUIDE yet. We're glad to walk your team through who qualifies, at no cost and with nothing to sign.</p>
    </div>
    <div class="card">
      <h3>Get the fifteen-minute version</h3>
      <p>Call {v("PHONE", "(405) phone")}{or_email()} and we'll come to you.</p>
    </div>
  </div>
</div></section>

{cta_band("You don't have to figure this out alone.", "Call and we'll go through the questions with you in about five minutes. Either way, you'll know where you stand.")}'''

LEAFLET = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" integrity="sha512-h9FcoyWjHcOcmEVkxOfTLnmZFWIH0iZhZT1H2TbOq55xssQGEJHEaIm+PgoUaZbRvQTNTluNOEfb1ZRy6D3BOw==" crossorigin="anonymous" referrerpolicy="no-referrer">',
           '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" integrity="sha512-puJW3E/qXDqYp9IfhAI54BJEaWIfloJ7JWs7OeD5i6ruC9JZL1gERT1wjtwXFlh7CjE7ZJ+/vcRZRkIYIb6p4g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>')

def page_outings():
    return f'''{LEAFLET[0]}
<link rel="stylesheet" href="assets/outings.css">
<section class="og-hero"><div class="shell og-hero-grid">
  <div>
    <p class="kicker">The Good Day Club &middot; Good days out</p>
    <h1>Care that gets them out the door.</h1>
    <p class="lede">A visit from us isn't only help around the house. It can be the book club at the Mustang library, lunch with friends at the Dale Robertson Center, a slow lap around Lake Overholser, or the gardens at Will Rogers Park. We drive, we stay with them, and we bring them home.</p>
    <div class="btn-row"><a class="btn" href="#og-builder-sec">Plan a sample week</a><a class="btn btn-outline" href="#og-explore">Explore places near you</a></div>
  </div>
  <ul class="og-hero-points">
    <li>{icon("i-car")}<b>We drive</b><span>Door to door in the caregiver's car, within our service area</span></li>
    <li>{icon("i-handshake")}<b>We stay</b><span>Right beside them the whole time, then home again</span></li>
    <li>{icon("i-pin")}<b>Real places</b><span>Senior centers, libraries, parks and events near you</span></li>
  </ul>
</div></section>

<section class="section"><div class="shell">
  <p class="kicker">How we add to their life</p>
  <h2>A week with something to look forward to.</h2>
  <p class="lede">When getting out gets harder, weeks shrink to the living room. Our caregivers help keep the world a little bigger.</p>
  <div class="og-pillars">
    <div>{icon("i-chat")}<h3>People to talk to</h3><p>Lunch at the senior center, a library book club, a friendly face every visit.</p></div>
    <div>{icon("i-strength")}<h3>Moving more</h3><p>Seated exercise at home, easy paved walks, chair yoga and fitness classes for older adults.</p></div>
    <div>{icon("i-book")}<h3>Learning and doing</h3><p>Museums, history, crafts, tech help at the library and classes worth showing up for.</p></div>
    <div>{icon("i-heart-honey")}<h3>Still part of things</h3><p>Festivals, farmers markets, church events and chances to give back in their own town.</p></div>
    <div>{icon("i-sun")}<h3>Fresh air</h3><p>Parks, gardens and lakeside benches. Twenty minutes outside can change a whole day.</p></div>
  </div>
</div></section>

<section class="section pale" id="og-builder-sec"><div class="shell">
  <p class="kicker">Try it</p>
  <h2>Plan a sample week.</h2>
  <p class="lede">Tell us a little about them, and we'll sketch what a week of visits could look like with real places close to home.</p>
  <div class="og-builder" id="og-builder">
    <div class="og-controls">
      <label>Their first name <span class="og-opt">(optional)</span><input id="og-name" maxlength="30" placeholder="For example, Mom or Ruth"></label>
      <label>Where they live<select id="og-home"></select></label>
      <label>Visits a week<select id="og-visits"><option value="1">One visit</option><option value="2" selected>Two visits</option><option value="3">Three visits</option></select></label>
      <fieldset><legend>What do they enjoy?</legend><div class="og-interests" id="og-interests"></div></fieldset>
      <button type="button" class="btn btn-outline" id="og-again">Show me other ideas</button>
    </div>
    <div class="og-week" id="og-week" aria-live="polite"></div>
  </div>
</div></section>

<section class="section" id="og-explore"><div class="shell">
  <p class="kicker">Explore</p>
  <h2>Places near you.</h2>
  <p class="lede">Real senior centers, libraries, parks, museums, classes and events in and around our service area. Tap a pin or a card for details.</p>
  <div class="og-filters">
    <div class="og-cats" id="og-cats" role="group" aria-label="Type of outing"></div>
    <div class="og-filter-row">
      <label class="og-search"><span class="sr-only">Search</span><input id="og-q" type="search" placeholder="Search, for example library or garden"></label>
      <label><span class="sr-only">Town</span><select id="og-town"><option value="all">All towns</option></select></label>
      <span class="og-count" id="og-count"></span>
    </div>
  </div>
  <div class="og-map-box"><div id="og-map" class="og-map" role="region" aria-label="Map of outing ideas"></div><p class="og-map-fallback">The map couldn't load. Every place is listed below.</p></div>
  <div class="og-grid" id="og-grid"><p class="og-empty">Loading places...</p></div>
  <p class="form-note" style="margin-top:18px">Hours, programs and prices change. We check each place's own website before we go, and you can too. Places listed aren't affiliated with Caring Companions.</p>
</div></section>

<section class="section alt"><div class="shell">
  <p class="kicker">Through the year</p>
  <h2>Something different every season.</h2>
  <p class="lede">Festivals and seasonal favorites around the area. Some fall on weekends or evenings, outside our visit hours, and make a wonderful family day.</p>
  <div class="og-cal" id="og-cal"></div>
</div></section>

<section class="section"><div class="shell">
  <div class="grid grid-2" style="align-items:start">
    <div>
      <p class="kicker">How outings work</p>
      <h2>Simple, safe and planned with you.</h2>
      <ul class="checks">
        <li>Outings happen during visits, Monday to Friday between 8am and 6pm.</li>
        <li>You approve each place before we go, and we write favorites into their service plan.</li>
        <li>The caregiver drives and stays with them the whole time.</li>
        <li>Admission, meals and class fees are paid by the family.</li>
        <li>On hot or icy days, we swap in an indoor plan.</li>
      </ul>
    </div>
    <div class="card">
      <h3>Who outings suit best</h3>
      <p>Our caregivers provide companion care, so they don't lift or physically support anyone. Outings work best for people who can walk and get in and out of a car on their own. A cane or walker is fine.</p>
      <p style="margin:0">Not sure? We'll talk it through at your free visit.</p>
    </div>
  </div>
</div></section>

{cta_band()}
{LEAFLET[1]}
<script src="assets/outings.js"></script>'''

def page_404():
    return f'''<section class="page-hero"><div class="shell">
  <p class="kicker">Page not found</p>
  <h1>We couldn't find that page.</h1>
  <p class="lede">It may have moved. Try one of these, or call us at {v("PHONE", "(405) phone")}.</p>
  <div class="btn-row" style="margin-top:18px"><a class="btn" href="/">Home</a><a class="btn btn-outline" href="/services.html">Services</a><a class="btn btn-outline" href="/join.html">Join the opening list</a></div>
</div></section>'''

# ---------- Town landing pages (local search) ----------
import math as _m
_OUT = json.load(open(os.path.join(ROOT, "assets", "outings.json")))["items"]
TOWN_INFO = [
    # slug, name, center, zips, county, minutes from the Mustang office, opening line
    ("mustang", "Mustang", (35.3842, -97.7245), ["73064"], "Canadian County", 2,
     "Mustang is home: our Oklahoma office is here, and every visit is planned from just down the road."),
    ("yukon", "Yukon", (35.5067, -97.7625), ["73099"], "Canadian County", 13,
     "Yukon families are about 13 minutes from our Mustang office, close enough for a caregiver who knows the town."),
    ("tuttle", "Tuttle", (35.2909, -97.8120), ["73089"], "Grady County", 22,
     "Tuttle is about 22 minutes from our Mustang office, and part of our everyday service area."),
    ("el-reno", "El Reno", (35.5323, -97.9550), ["73036"], "Canadian County", 28,
     "El Reno is about 28 minutes from our Mustang office, with a downtown full of history worth getting out to see."),
    ("piedmont", "Piedmont", (35.6420, -97.7464), ["73078"], "Canadian County", 37,
     "Piedmont is at the north edge of our service area, about 37 minutes from our Mustang office."),
    ("bethany", "Bethany", (35.5187, -97.6323), ["73008"], "Oklahoma County", 20,
     "Bethany is about 20 minutes from our Mustang office, with a library, parks and a YMCA all close to home."),
    ("nichols-hills", "Nichols Hills", (35.5509, -97.5489), ["73116"], "Oklahoma County", 29,
     "Nichols Hills is about 29 minutes from our Mustang office, near Lake Hefner, Will Rogers Park and some of the area's best libraries."),
    ("oklahoma-city", "Oklahoma City", (35.4580, -97.6480), ["73127", "73128", "73169", "73179", "73159", "73170", "73173", "73132", "73162", "73142"], "Oklahoma and Cleveland counties", None,
     "We serve west, southwest and northwest Oklahoma City, most of it within 25 minutes of our Mustang office."),
]
CAT_LABEL = {"senior-center": "Senior center", "library": "Library", "park-garden": "Park or garden", "museum-history": "Museum and history",
             "arts-music-classes": "Arts and music", "exercise": "Staying active", "events-seasonal": "Event", "everyday": "Everyday outing", "volunteering": "Giving back"}

def _mi(a, b):
    t = _m.pi / 180; dl = (b[0] - a[0]) * t; do = (b[1] - a[1]) * t
    h = _m.sin(dl / 2) ** 2 + _m.cos(a[0] * t) * _m.cos(b[0] * t) * _m.sin(do / 2) ** 2
    return 2 * 3958.8 * _m.asin(_m.sqrt(h))

def town_places(center, n=6):
    pool = [(_mi(center, (x["lat"], x["lon"])), x) for x in _OUT if x.get("lat") and not x.get("family") and x["category"] != "events-seasonal"]
    pool.sort(key=lambda z: z[0])
    picked, seen = [], set()
    for d, x in pool:                      # variety first: one per category
        if x["category"] in seen: continue
        seen.add(x["category"]); picked.append((d, x))
        if len(picked) == n: break
    for d, x in pool:                      # then fill with the nearest
        if len(picked) == n: break
        if (d, x) not in picked: picked.append((d, x))
    return sorted(picked, key=lambda z: z[0])

def town_schema(name, slug):
    data = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Companion care for older adults",
            "name": f"Companion care in {name}, OK", "url": f'{CONFIG["DOMAIN"]}/companion-care-{slug}-ok',
            "provider": {"@type": "LocalBusiness", "name": "Caring Companions Oklahoma", "url": CONFIG["DOMAIN"] + "/",
                         "telephone": "+1-405-500-1758", "address": {"@type": "PostalAddress", "addressLocality": "Mustang", "addressRegion": "OK", "postalCode": "73064", "addressCountry": "US"}},
            "areaServed": {"@type": "City", "name": f"{name}, OK"},
            "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "18:00"}}
    return '<script type="application/ld+json">' + json.dumps(data) + '</script>'

def make_town_page(t):
    slug, name, center, zips, county, mins, opener = t
    places = town_places(center)
    cards = "".join(
        f'<a class="card card-link" href="{html.escape(x.get("website") or "outings.html")}" target="_blank" rel="noopener">'
        f'<p class="kicker" style="margin-bottom:6px">{CAT_LABEL.get(x["category"], "Outing")}</p><h3>{html.escape(x["name"])}</h3>'
        f'<p>{html.escape(x["town"])}, about {max(1, round(d))} mile{"s" if round(d) != 1 else ""} away</p></a>' for d, x in places)
    zip_list = ", ".join(zips)
    others = "".join(f'<li><a href="companion-care-{o[0]}-ok.html">{o[1]}</a></li>' for o in TOWN_INFO if o[0] != slug)
    time_line = f"about {mins} minutes from our Mustang office" if mins is not None else "within about 25 minutes of our Mustang office"
    def page():
        return f'''{town_schema(name, slug)}
<section class="page-hero"><div class="shell">
  <p class="kicker">Companion care in {name}, Oklahoma <span class="open-chip">Opening {CONFIG["OPENING"]}</span></p>
  <h1>Weekday companion care in {name}.</h1>
  <p class="lede">{opener} A regular companion for Mom or Dad, Monday to Friday between 8 and 6: good company, a hot lunch, errands done and a ride to the doctor.</p>
  <div class="btn-row" style="margin-top:18px"><a class="btn" href="join.html">Join the opening list</a><a class="btn btn-outline" href="{phone_href()}">Call {v("PHONE", "(405) phone")}</a></div>
</div></section>

<section class="section"><div class="shell grid grid-2" style="align-items:start">
  <div>
    <h2>What we help with in {name}</h2>
    <ul class="checks">
      <li>Companionship: conversation, games, hobbies and walks</li>
      <li>Light housekeeping, laundry and meals cooked at home</li>
      <li>Errands, groceries and rides to appointments</li>
      <li>A guided seated exercise routine and medication reminders</li>
      <li>Respite, so the family caregiver gets a break</li>
    </ul>
    <p>All of it is part of <a href="index.html#good-day-club">The Good Day Club</a>, our way of helping older adults stay independent longer. Companion care is $30 an hour, starting with one 4-hour visit a week. <a href="pricing.html">See pricing</a></p>
  </div>
  <div class="card">
    <h3>Serving {name}</h3>
    <dl class="hours"><dt>ZIP codes</dt><dd>{zip_list}</dd><dt>County</dt><dd>{county}</dd><dt>Distance</dt><dd>{time_line}</dd><dt>Visits</dt><dd>Monday to Friday, 8am to 6pm</dd></dl>
    <p style="margin:0"><a href="service-area.html">Check your ZIP on our map</a></p>
  </div>
</div></section>

<section class="section alt"><div class="shell">
  <p class="kicker">Good days out near {name}</p>
  <h2>Places we can go together.</h2>
  <p class="lede">A visit can include an outing. Here are a few real places close to {name}. Our caregiver drives, stays with them, and brings them home.</p>
  <div class="grid grid-3" style="margin-top:22px">{cards}</div>
  <p style="margin-top:18px"><a href="outings.html">See all outing ideas and plan a sample week</a></p>
</div></section>

<section class="section"><div class="shell" style="max-width:860px">
  <h2>Questions families in {name} ask</h2>
  <div class="faqs">
    <details class="faq"><summary>Do you serve all of {name}?</summary><p>We serve ZIP code{"s" if len(zips) > 1 else ""} {zip_list}. If you're not sure about your address, call us at {v("PHONE", "(405) phone")} or check your ZIP on our <a href="service-area.html">service area map</a>.</p></details>
    <details class="faq"><summary>When can visits start?</summary><p>We're licensed and open in Mustang in {CONFIG["OPENING"]}. <a href="join.html">Join the opening list</a> and we'll be in touch as opening gets closer.</p></details>
    <details class="faq"><summary>Do your caregivers help with bathing or dressing?</summary><p>No. Our Oklahoma license is for companion services, so our caregivers don't give hands-on personal care. If your loved one needs that, we'll tell you honestly at the first visit.</p></details>
    <details class="faq"><summary>Does Medicare pay for any of this?</summary><p>Regular companion care is paid privately. For families living with dementia, Medicare's <a href="medicare-guide.html">GUIDE program</a> may cover respite visits.</p></details>
  </div>
</div></section>

<section class="section tight alt"><div class="shell">
  <h2>Other towns we serve</h2>
  <ul class="towns town-links">{others}</ul>
</div></section>

{cta_band()}'''
    return page

TOWN_PAGES = [(f"companion-care-{t[0]}-ok.html", f"Companion Care in {t[1]}, OK | Caring Companions Oklahoma",
               f"Weekday companion care for older adults in {t[1]}, Oklahoma: company, meals, errands, rides and seated exercise. $30/hour. Opening June 2027.",
               make_town_page(t)) for t in TOWN_INFO]

PAGES = [
    ("index.html", "Weekday Companion Care in Mustang, OK | Caring Companions",
     "Weekday companion care in Mustang, OK. The Good Day Club helps older adults stay independent longer: company, meals, gentle exercise, errands and rides to appointments. Monday to Friday, 8 to 6.", page_index),
    ("services.html", "Companion Care Services | Caring Companions Oklahoma",
     "Companionship, light housekeeping, meal preparation, errands, rides to appointments, medication reminders and respite for families in Mustang, OK.", page_services),
    ("pricing.html", "Companion Care Pricing | Caring Companions Oklahoma",
     "One simple hourly rate for companion care in Mustang, OK. Free first visit at home, no obligation.", page_pricing),
    ("getting-started.html", "Getting Started | Caring Companions Oklahoma",
     "What happens after you call: a free visit at home, a written service plan, a matched caregiver, and care that begins on your schedule.", page_getting_started),
    ("service-area.html", "Service Area | Caring Companions Oklahoma",
     "Weekday companion care in Mustang, Yukon, Tuttle, El Reno, Piedmont, Bethany, Nichols Hills and west, southwest and northwest Oklahoma City.", page_service_area),
    ("outings.html", "Senior Outings & Activities in Mustang, OK | Caring Companions",
     "Senior centers, libraries, parks, museums, classes and events near Mustang, Yukon and west Oklahoma City, and how our companion caregivers take your loved one there.", page_outings),
    ("resources.html", "Family Resources | Caring Companions Oklahoma",
     "Free dementia course, planning tools and guides for families caring for an aging parent.", page_resources),
] + ([("medicare-guide.html", "Medicare GUIDE Dementia Respite | Caring Companions Oklahoma",
     "Medicare's GUIDE program may pay for dementia respite visits for families in Mustang and west Oklahoma City. See who qualifies.", page_guide)] if CONFIG["GUIDE"] else []) + [
    ("about.html", "About Us | Caring Companions Oklahoma",
     "A family-owned company caring for families since 2017, now serving Mustang, Oklahoma with companion care.", page_about),
    ("careers.html", "Now Hiring: Companion Caregiver Jobs in Mustang, OK | Caring Companions",
     "Now hiring companion caregivers in Mustang, Oklahoma. Weekday daytime hours, no nights, no weekends. Apply in two minutes, no resume needed.", page_careers),
    ("contact.html", "Contact Us | Caring Companions Oklahoma",
     "Reach Caring Companions in Mustang, OK, or join our opening list. Weekday companion care opening June 2027.", page_contact),
    ("join.html", "Join Our Opening List | Caring Companions Oklahoma",
     "Caring Companions opens in Mustang, Oklahoma in June 2027. Join the opening list as a family, a future caregiver or a referral partner.", page_join),
]

def build():
    for fname, title, desc, fn in PAGES + TOWN_PAGES + [("404.html", "Page Not Found | Caring Companions Oklahoma", "Page not found.", page_404)]:
        body = fn()
        with open(os.path.join(ROOT, fname), "w") as f:
            f.write(head(fname, title, desc) + header(fname) + body + footer())
    robots = ("User-agent: *\nDisallow: /\n" if CONFIG["PREVIEW"]
              else f"User-agent: *\nAllow: /\nSitemap: {CONFIG['DOMAIN']}/sitemap.xml\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(robots)
    urls = "".join(
        f"<url><loc>{CONFIG['DOMAIN']}/{'' if p == 'index.html' else p.replace('.html', '')}</loc></url>"
        for p, *_ in PAGES + TOWN_PAGES)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')

if __name__ == "__main__":
    build()
    missing = sorted(set(MISSING))
    if "--check" in sys.argv:
        print("Still to fill in:" if missing else "Nothing missing.", *missing, sep="\n  ")
        if CONFIG["PREVIEW"]:
            print("PREVIEW is still True (site is hidden from search engines).")
        sys.exit(1 if missing or CONFIG["PREVIEW"] else 0)
    print(f"Built {len(PAGES)} pages. Placeholders left: {', '.join(missing) or 'none'}")
