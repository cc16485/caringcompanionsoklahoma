// Caring Companions Oklahoma: the Companion application (806, Samantha 2026-10-16: "Approve the Oklahoma Companion
// pre-screener plan with all six decisions as you recommended").
// Three short screens. It saves into the Hub's applicant list through the same public save the Missouri apply page uses
// (apply_save: insert only, the database decides everything else), as the position "Companion", so the Hub marks the
// person Oklahoma. It saves after screen 1, so somebody who stops halfway is still a person the recruiter can call.
// Nothing here texts or emails anyone. Interviews are set up by phone (no booking here: there is no Mustang office yet).
(function () {
  'use strict';
  var C = Object.assign({
    rpc: 'https://zngsgedlsxinbygwmxwn.supabase.co/rest/v1/rpc/apply_save',
    key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpuZ3NnZWRsc3hpbmJ5Z3dteHduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI1NDIzNDQsImV4cCI6MjA5ODExODM0NH0.L_31_UKdccyRH9n7p1GaBlZTqcJipB008H-GIvxwLxM',
    phone: '(405) 500-1758', towns: {}
  }, window.APPLY_CONFIG || {});
  var form = document.querySelector('form[data-apply]'); if (!form) return;
  var steps = form.querySelectorAll('[data-step]'), status = form.querySelector('.join-status'), id = null, A = {};
  var KEY = 'cc_ok_apply_id';
  try { id = sessionStorage.getItem(KEY) || null; } catch (e) { id = null; }
  var src = (new URLSearchParams(location.search).get('src') || '').replace(/[^\w .-]/g, '').slice(0, 60);

  function show(n) {
    steps.forEach(function (s) { s.hidden = s.getAttribute('data-step') !== String(n); });
    var bar = form.querySelector('.apply-progress'); if (bar) bar.textContent = typeof n === 'number' ? 'Step ' + n + ' of 3' : '';
    status.textContent = ''; status.className = 'join-status';
    var first = form.querySelector('[data-step="' + n + '"] input, [data-step="' + n + '"] select');
    try { form.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) { /* older browsers */ }
    if (first && n !== 1) setTimeout(function () { try { first.focus({ preventScroll: true }); } catch (e) {} }, 300);
  }
  function err(msg) { status.className = 'join-status err'; status.textContent = msg; }
  function val(name) { var el = form.querySelector('[name="' + name + '"]:checked') || form.querySelector('[name="' + name + '"]:not([type=radio])'); return el ? String(el.value || '').trim() : ''; }
  function yn(name) { var v = val(name); return v === 'yes' ? true : v === 'no' ? false : null; }
  function save(data, done) {
    return fetch(C.rpc, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: C.key, Authorization: 'Bearer ' + C.key },
      body: JSON.stringify({ p_id: id, p_data: data, p_done: !!done })
    }).then(function (r) {
      return r.json().catch(function () { return null; }).then(function (j) {
        if (!r.ok) { var m = (j && (j.message || j.hint)) || ('HTTP ' + r.status); throw new Error(m); }
        return j;
      });
    });
  }
  /* the saved start is no longer open (finished, or closed by the office): start a fresh one */
  function gone() { id = null; try { sessionStorage.removeItem(KEY); } catch (e) {} show(1); err('That application is already closed. Please start again here.'); }
  function busy(btn, on) { btn.disabled = on; btn.dataset.label = btn.dataset.label || btn.textContent; btn.textContent = on ? 'Saving...' : btn.dataset.label; }
  function failed(e) {
    if (/NOSHOW_BEFORE/.test(String(e && e.message || e))) {
      err('Our records show a missed interview with us before, so we are not able to take a new application online. Please call us on ' + C.phone + '.');
    } else err('Sorry, that did not save. Please try again, or call us on ' + C.phone + '.');
  }

  form.addEventListener('click', function (e) {
    var b = e.target.closest('[data-go]'); if (!b) return;
    e.preventDefault();
    var go = b.getAttribute('data-go');
    if (go === 'back2') return show(1);
    if (go === 'back3') return show(2);
    if (go === '1') {
      if (form.querySelector('[name="website"]').value) return;   // honeypot
      var first = val('first_name'), last = val('last_name'), phone = val('phone'), email = val('email'), zip = val('zip').replace(/\D/g, '');
      if (!first || !last) return err('Please add your first and last name.');
      if (phone.replace(/\D/g, '').length < 10) return err('Please add a phone number we can call (10 digits).');
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return err('Please check the email address.');
      if (zip.length !== 5) return err('Please add your 5-digit ZIP code.');
      var d1 = { first_name: first.slice(0, 80), last_name: last.slice(0, 80), phone: phone.slice(0, 40), email: email ? email.slice(0, 200) : null, zip: zip,
        city: C.towns[zip] || null, sms_consent: !!form.querySelector('[name="sms"]').checked };
      busy(b, true);
      var p = id ? save(d1, false) : save(Object.assign({ position: 'companion', posting_title: 'Companion', source: 'website',
        channel: src || 'caringcompanionsoklahoma.com' }, d1), false);
      p.then(function (r) {
        if (id && !r) { id = null; return save(Object.assign({ position: 'companion', posting_title: 'Companion', source: 'website',
          channel: src || 'caringcompanionsoklahoma.com' }, d1), false); }
        return r;
      }).then(function (r) {
        if (!id) { id = r; try { sessionStorage.setItem(KEY, id); } catch (e2) {} }
        if (!id) throw new Error('no id');
        show(2);
      }).catch(failed).finally(function () { busy(b, false); });
      return;
    }
    if (go === '2') {
      var age = yn('age_ok'), auth = yn('work_auth'), oks = yn('okscreen'), wk = val('weekdays'), drive = yn('drive'), exp = val('experience_years'), start = val('start');
      if (age === null || auth === null || oks === null || !wk || drive === null || !exp || !start) return err('Please answer every question.');
      A = { 'OKSCREEN fingerprint check': oks ? 'Yes' : 'No', 'Weekday hours, 8am to 6pm': wk, 'Drive clients (license, car, insurance)': drive ? 'Yes' : 'No', 'When can you start': start };
      var d2 = { age_ok: age, work_auth: auth, can_pass_background: oks, has_transport: drive, has_license: drive ? true : null, has_insurance: drive ? true : null,
        experience_years: exp, availability: wk === 'All weekdays' ? 'All weekdays, 8am to 6pm' : wk === 'Some weekdays' ? 'Some weekdays, between 8am and 6pm' : 'No weekday hours',
        role_answers: A };
      var stop = age === false ? ['under 18', 'Our caregivers need to be 18 or older, so we are not able to take your application further right now.', 'If you are turning 18 soon, please apply again then. We would be glad to hear from you.']
        : auth === false ? ['not authorized to work in the US', 'We are only able to hire people who are authorized to work in the United States.', 'If your situation changes, you would be welcome to apply again.']
        : oks === false ? ['would not agree to the OKSCREEN fingerprint check', 'Every caregiver in Oklahoma has to pass an OKSCREEN fingerprint background check before working with clients, so we are not able to take your application further.', 'If you change your mind, you would be welcome to apply again.']
        : wk === 'No weekday hours' ? ['no weekday hours between 8am and 6pm', 'All of our visits are on weekdays between 8am and 6pm, so we are not able to offer you work right now.', 'If your weekdays open up, please apply again.']
        : null;
      if (stop) d2.decline_reason = stop[0];
      busy(b, true);
      save(d2, false).then(function (r) {
        if (!r) return gone();
        if (stop) {
          try { sessionStorage.removeItem(KEY); } catch (e2) {}
          form.querySelector('[data-stop-why]').textContent = stop[1];
          form.querySelector('[data-stop-next]').textContent = stop[2] + ' Questions? Call us on ' + C.phone + '.';
          return show('stop');
        }
        show(3);
      }).catch(failed).finally(function () { busy(b, false); });
      return;
    }
    if (go === '3') {
      var more = val('anything_else');
      var d3 = { experience: val('enjoy').slice(0, 2000) || null, referral_source: val('referral_source') || null,
        role_answers: Object.assign({}, A, more ? { 'Anything else': more.slice(0, 2000) } : {}) };
      busy(b, true);
      save(d3, true).then(function (r) {
        if (!r) return gone();
        try { sessionStorage.removeItem(KEY); } catch (e2) {}
        show('done');
        try { if (window.ccTrack) window.ccTrack('apply_done', { site: 'oklahoma', position: 'companion' }); } catch (e3) {}
      }).catch(failed).finally(function () { busy(b, false); });
    }
  });
  show(id ? 2 : 1);
})();
