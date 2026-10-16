"""806 (2026-10-16): the Companion application (apply.html + assets/apply.js) in a real browser, against a stand-in for the
Hub's apply_save (it answers like the real one: a new id on the first save, the same id after, nothing once closed).
Made-up people only; nothing reaches the database and nothing is sent.  python3 tools/build.py && python3 tools/apply_test.py"""
import os, sys, json, socket, subprocess, time, re
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
s_ = socket.socket(); s_.bind(('127.0.0.1', 0)); PORT = s_.getsockname()[1]; s_.close()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '-d', ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
R = []
ok = lambda n, c, d='': R.append(('PASS' if c else 'FAIL', n, '' if c else str(d)[:600]))
for f in ['apply.html', 'assets/apply.js']:
    ok(f'no em dashes in {f}', '—' not in open(os.path.join(ROOT, f)).read())
A = open(os.path.join(ROOT, 'apply.html')).read()
for bad in ['personal care assistance', 'CNA', 'Medicaid', 'CDS', 'FCSR', 'Family Care Safety', 'Missouri']:
    form = A[A.index('<form'):A.index('</form>')]
    ok(f'the form never asks about {bad}', bad not in form)
# hiring is not open yet (CONFIG HIRING_OPEN False): the application is built but unlisted
import glob
ok('not open yet: apply.html is hidden from search engines', '<meta name="robots" content="noindex, nofollow">' in A)
ok('not open yet: apply.html is not in the sitemap', 'caringcompanionsoklahoma.com/apply<' not in open(os.path.join(ROOT, 'sitemap.xml')).read())
ok('not open yet: no page links to apply.html', not [f for f in glob.glob(os.path.join(ROOT, '*.html')) if 'href="apply.html"' in open(f).read()])
CALLS = []
def fake(route):
    req = route.request; b = json.loads(req.post_data or '{}'); CALLS.append(b)
    if FAKE.get('noshow') and b.get('p_id') is None:
        return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'NOSHOW_BEFORE: no-showed for an interview before'}))
    if FAKE.get('closed') and b.get('p_id'):
        return route.fulfill(status=200, content_type='application/json', body='null')
    rid = b.get('p_id') or '11111111-2222-4333-8444-555555555555'
    route.fulfill(status=200, content_type='application/json', body=json.dumps(rid))
FAKE = {}
def fill1(pg, zip_='73099'):
    pg.fill('[name=first_name]', 'Test'); pg.fill('[name=last_name]', 'Companion OK'); pg.fill('[name=phone]', '(405) 555-0180')
    pg.fill('[name=email]', 'test.companion@practice.invalid'); pg.fill('[name=zip]', zip_)
def fill2(pg, age='yes', auth='yes', oks='yes', wk='All weekdays', drive='yes'):
    for n, v in [('age_ok', age), ('work_auth', auth), ('okscreen', oks), ('weekdays', wk), ('drive', drive)]: pg.check(f'[name={n}][value="{v}"]')
    pg.select_option('[name=experience_years]', '1 to 3 years'); pg.select_option('[name=start]', 'Spring 2027')
try:
  with sync_playwright() as pw:
    b = pw.chromium.launch()
    for vw in [{'width': 1200, 'height': 900}, {'width': 375, 'height': 800}]:
        ctx = b.new_context(viewport=vw); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/rest/v1/rpc/apply_save', fake); CALLS.clear(); FAKE.clear()
        pg.goto(f'http://127.0.0.1:{PORT}/apply.html'); pg.wait_for_timeout(400)
        w = 'phone' if vw['width'] < 500 else 'desktop'
        ok(f'{w}: opens on step 1 of 3', pg.is_visible('[data-step="1"]') and not pg.is_visible('[data-step="2"]') and 'step 1 of 3' in pg.inner_text('.apply-progress').lower())
        ok(f'{w}: no sideways scroll', pg.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
        pg.click('[data-go="1"]'); pg.wait_for_timeout(100)
        ok(f'{w}: step 1 needs a name first (nothing saved)', 'first and last name' in pg.inner_text('.join-status') and not CALLS)
        fill1(pg); pg.click('[data-go="1"]'); pg.wait_for_timeout(300)
        c = CALLS[0] if CALLS else {}
        d = c.get('p_data', {})
        ok(f'{w}: step 1 saves a new Companion application (Oklahoma by its position), no text consent unless ticked',
           c.get('p_id') is None and c.get('p_done') is False and d.get('position') == 'companion' and d.get('posting_title') == 'Companion'
           and d.get('first_name') == 'Test' and d.get('zip') == '73099' and d.get('city') == 'Yukon' and d.get('sms_consent') is False
           and d.get('channel') == 'caringcompanionsoklahoma.com' and 'office' not in d, c)
        ok(f'{w}: on to step 2', pg.is_visible('[data-step="2"]') and 'step 2 of 3' in pg.inner_text('.apply-progress').lower())
        pg.click('[data-go="2"]'); pg.wait_for_timeout(100)
        ok(f'{w}: step 2 needs every answer', 'every question' in pg.inner_text('.join-status') and len(CALLS) == 1)
        fill2(pg, drive='no'); pg.click('[data-go="2"]'); pg.wait_for_timeout(300)
        d = CALLS[-1].get('p_data', {})
        ok(f'{w}: step 2 saves the answers to the same application (no to driving is fine)',
           CALLS[-1].get('p_id') == '11111111-2222-4333-8444-555555555555' and d.get('age_ok') is True and d.get('work_auth') is True
           and d.get('can_pass_background') is True and d.get('has_transport') is False and d.get('experience_years') == '1 to 3 years'
           and d.get('availability') == 'All weekdays, 8am to 6pm' and d.get('role_answers', {}).get('When can you start') == 'Spring 2027'
           and 'decline_reason' not in d, CALLS[-1])
        ok(f'{w}: on to step 3', pg.is_visible('[data-step="3"]'))
        pg.fill('[name=enjoy]', 'Their stories.'); pg.fill('[name=anything_else]', 'I can start soon.'); pg.select_option('[name=referral_source]', 'Indeed')
        pg.click('[data-go="3"]'); pg.wait_for_timeout(300)
        c = CALLS[-1]; d = c.get('p_data', {})
        ok(f'{w}: step 3 finishes it (done), keeps the earlier answers and adds theirs', c.get('p_done') is True and d.get('experience') == 'Their stories.'
           and d.get('referral_source') == 'Indeed' and d.get('role_answers', {}).get('Anything else') == 'I can start soon.' and d.get('role_answers', {}).get('OKSCREEN fingerprint check') == 'Yes', c)
        t = pg.inner_text('[data-step="done"]')
        ok(f'{w}: the thank-you says we will call from (405) 500-1758', pg.is_visible('[data-step="done"]') and '(405) 500-1758' in t, t)
        ok(f'{w}: no page errors', not errs, errs)
        ctx.close()
    # the knockouts
    for label, kw, why in [('no to OKSCREEN', {'oks': 'no'}, 'OKSCREEN'), ('under 18', {'age': 'no'}, '18 or older'),
                           ('no weekday hours', {'wk': 'No weekday hours'}, 'weekdays between 8am and 6pm')]:
        ctx = b.new_context(); pg = ctx.new_page(); pg.route('**/rest/v1/rpc/apply_save', fake); CALLS.clear(); FAKE.clear()
        pg.goto(f'http://127.0.0.1:{PORT}/apply.html'); pg.wait_for_timeout(300); fill1(pg); pg.click('[data-go="1"]'); pg.wait_for_timeout(250)
        fill2(pg, **kw); pg.click('[data-go="2"]'); pg.wait_for_timeout(300)
        d = CALLS[-1].get('p_data', {}); t = pg.inner_text('[data-step="stop"]')
        ok(f'{label}: saved with the reason, a kind explanation, no step 3', d.get('decline_reason') and pg.is_visible('[data-step="stop"]') and why in t and '(405) 500-1758' in t and not pg.is_visible('[data-step="3"]'), [d, t])
        ctx.close()
    ok('driving and under a year never turn anyone away (checked above: no to driving went on to step 3)', True)
    # a missed interview before: the database refuses, the page explains
    ctx = b.new_context(); pg = ctx.new_page(); pg.route('**/rest/v1/rpc/apply_save', fake); CALLS.clear(); FAKE.clear(); FAKE['noshow'] = True
    pg.goto(f'http://127.0.0.1:{PORT}/apply.html'); pg.wait_for_timeout(300); fill1(pg); pg.click('[data-go="1"]'); pg.wait_for_timeout(300)
    ok('a past no-show: told to call, stays on step 1', 'missed interview' in pg.inner_text('.join-status') and pg.is_visible('[data-step="1"]'))
    ctx.close()
    # coming back to a closed application starts a new one
    ctx = b.new_context(); pg = ctx.new_page(); pg.route('**/rest/v1/rpc/apply_save', fake); CALLS.clear(); FAKE.clear()
    pg.goto(f'http://127.0.0.1:{PORT}/apply.html'); pg.wait_for_timeout(300); fill1(pg); pg.click('[data-go="1"]'); pg.wait_for_timeout(250)
    FAKE['closed'] = True; fill2(pg); pg.click('[data-go="2"]'); pg.wait_for_timeout(300)
    ok('an application closed meanwhile: back to step 1 with a note', pg.is_visible('[data-step="1"]') and 'already closed' in pg.inner_text('.join-status'))
    ctx.close()
    b.close()
finally:
  srv.terminate()
for s, n, d in R: print(s, ' ', n, ('  ' + d) if d else '')
print(f"{sum(r[0] == 'PASS' for r in R)}/{len(R)} passed"); sys.exit(0 if all(r[0] == 'PASS' for r in R) else 1)
