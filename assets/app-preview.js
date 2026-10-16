// Caring Companions: interactive preview of the visit-booking app (sample data, nothing is booked).
// Open with any element that has [data-app-preview]. Per-site settings come from window.AP_CONFIG.
(function () {
  'use strict';
  var C = Object.assign({
    brand: 'Caring Companions',
    tagline: 'The Good Day Club',
    weekdaysOnly: true,
    startHour: 8, endHour: 18,
    minHours: 4,
    rate: 30,
    rateLabel: 'Companion care',
    joinHref: 'join.html',
    joinLabel: 'Join the opening list',
    footnote: 'Preview with sample information. The app launches when we open.',
    icons: 'assets/icons.svg',
    activities: [
      { k: 'exercise', t: 'Seated exercise', i: 'i-strength' },
      { k: 'lunch', t: 'Cook lunch together', i: 'i-bowl' },
      { k: 'meds', t: 'Medication reminder', i: 'i-clock' },
      { k: 'outing', t: 'An outing', i: 'i-car' },
      { k: 'errands', t: 'Errands and groceries', i: 'i-bag' },
      { k: 'house', t: 'Light housekeeping', i: 'i-home' },
      { k: 'chat', t: 'Cards, games and conversation', i: 'i-chat' }
    ],
    // Sample caregivers for the preview only (not real people).
    caregivers: [
      { k: 'linda', n: 'Linda', ini: 'LM', c: '#1F7A8C', yrs: '6 years caring for older adults', town: 'Mustang',
        hi: 'Retired school secretary. I love a good card game, my garden and cooking Sunday-style lunches on a Tuesday.',
        likes: ['Gardening', 'Card games', 'Home cooking'], drives: true },
      { k: 'marcus', n: 'Marcus', ini: 'MT', c: '#0D365F', yrs: '3 years as a companion', town: 'Yukon',
        hi: 'I play guitar, follow the Thunder and never mind a long drive to an appointment. Patient and easy to talk to.',
        likes: ['Music', 'Sports', 'Walks'], drives: true },
      { k: 'rosa', n: 'Rosa', ini: 'RG', c: '#C17A12', yrs: '4 years caring for older adults', town: 'Tuttle',
        hi: 'Baker, walker and talker. I speak English and Spanish and I love hearing the old stories.',
        likes: ['Baking', 'Crafts', 'Old movies'], drives: false }
    ]
  }, window.AP_CONFIG || {});

  var DAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var DAYL = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function ic(id) { return '<svg class="ap-ic" aria-hidden="true"><use href="' + C.icons + '#' + id + '"/></svg>'; }
  function hr(h) { var ap = h >= 12 ? 'pm' : 'am', x = h % 12 || 12; return x + ap; }

  var st, root, screen, lastFocus;
  function reset() {
    st = { step: 0, day: null, start: null, hours: C.minHours, acts: ['exercise', 'lunch', 'meds'], who: 'Mom', repeat: true, cg: null, view: null };
  }
  function days() {
    var out = [], d = new Date(); d.setHours(12, 0, 0, 0);
    while (out.length < 10) {
      d.setDate(d.getDate() + 1);
      if (C.weekdaysOnly && (d.getDay() === 0 || d.getDay() === 6)) continue;
      out.push(new Date(d));
    }
    return out;
  }

  var STEPS = [welcome, pickDay, pickTime, plan, pickCaregiver, review, booked];
  var TOTAL = 5;
  function cgBy(k) { return C.caregivers.filter(function (c) { return c.k === k; })[0]; }
  function av(c, big) { return '<span class="ap-av' + (big ? ' big' : '') + '" style="background:' + c.c + '" aria-hidden="true">' + c.ini + '</span>'; }

  function welcome() {
    return '<div class="ap-hello"><p class="ap-kicker">' + C.tagline + '</p><h3>Book a visit in a minute.</h3>' +
      '<p>Pick a day, choose what they’d like to do, and you’re set.</p>' +
      '<label class="ap-field">Who is the visit for?<select data-k="who"><option>Mom</option><option>Dad</option><option>Grandma</option><option>Grandpa</option><option>Myself</option></select></label>' +
      '<div class="ap-list-preview"><span>' + ic('i-calendar') + 'Upcoming visits</span><b>Nothing booked yet</b></div></div>' +
      foot('<button class="ap-btn" data-go="1">Book a visit</button>');
  }
  function pickDay() {
    var ds = days();
    return head('When should we come?') + '<div class="ap-days">' + ds.map(function (d, i) {
      var sel = st.day && st.day.getTime() === d.getTime();
      return '<button class="ap-day' + (sel ? ' on' : '') + '" data-day="' + i + '"><small>' + DAY[d.getDay()] + '</small><b>' + d.getDate() + '</b><small>' + MON[d.getMonth()] + '</small></button>';
    }).join('') + '</div>' +
    (C.weekdaysOnly ? '<p class="ap-note">Visits run Monday to Friday, ' + hr(C.startHour) + ' to ' + hr(C.endHour) + '.</p>' : '<p class="ap-note">Mornings, evenings or weekends, whatever fits.</p>') +
    '<label class="ap-check"><input type="checkbox" data-k="repeat"' + (st.repeat ? ' checked' : '') + '> Repeat every week</label>' +
    foot('<button class="ap-btn" data-go="2"' + (st.day ? '' : ' disabled') + '>Next</button>');
  }
  function pickTime() {
    var slots = [];
    for (var h = C.startHour; h + st.hours <= C.endHour; h++) slots.push(h);
    return head('What time, and how long?') +
      '<div class="ap-len">' + [4, 5, 6, 8].filter(function (n) { return n >= C.minHours && C.startHour + n <= C.endHour; }).map(function (n) {
        return '<button class="ap-pill' + (st.hours === n ? ' on' : '') + '" data-hours="' + n + '">' + n + ' hours</button>';
      }).join('') + '</div>' +
      '<div class="ap-slots">' + slots.map(function (h) {
        return '<button class="ap-slot' + (st.start === h ? ' on' : '') + '" data-start="' + h + '">' + hr(h) + ' to ' + hr(h + st.hours) + '</button>';
      }).join('') + '</div>' +
      '<p class="ap-note">Every visit is at least ' + C.minHours + ' hours, so there’s time to do things properly.</p>' +
      foot('<button class="ap-btn ap-ghost" data-go="1">Back</button><button class="ap-btn" data-go="3"' + (st.start != null ? '' : ' disabled') + '>Next</button>');
  }
  function plan() {
    return head('What would ' + esc(st.who === 'Myself' ? 'you' : st.who) + ' like to do?') +
      '<div class="ap-acts">' + C.activities.map(function (a) {
        var on = st.acts.indexOf(a.k) > -1;
        return '<button class="ap-act' + (on ? ' on' : '') + '" data-act="' + a.k + '">' + ic(a.i) + '<span>' + a.t + '</span><i></i></button>';
      }).join('') + '</div>' +
      foot('<button class="ap-btn ap-ghost" data-go="2">Back</button><button class="ap-btn" data-go="4"' + (st.acts.length ? '' : ' disabled') + '>Next</button>');
  }
  function pickCaregiver() {
    if (st.view) return profile(cgBy(st.view));
    return head('Who would you like to come?') +
      '<div class="ap-cgs">' + C.caregivers.map(function (c) {
        return '<div class="ap-cg' + (st.cg === c.k ? ' on' : '') + '">' + av(c) +
          '<button class="ap-cg-pick" data-cg="' + c.k + '"><b>' + c.n + '</b><small>' + c.yrs + '</small></button>' +
          '<button class="ap-link" data-view="' + c.k + '">Profile</button></div>';
      }).join('') +
      '<button class="ap-cg ap-cg-any' + (st.cg === 'any' ? ' on' : '') + '" data-cg="any"><span class="ap-av" style="background:#8a96a3" aria-hidden="true">?</span><span><b>Whoever is available</b><small>We’ll pick a great match and show you their profile</small></span></button></div>' +
      '<p class="ap-note">Sample caregivers for this preview. Every real caregiver passes a fingerprint background check.</p>' +
      foot('<button class="ap-btn ap-ghost" data-go="3">Back</button><button class="ap-btn" data-go="5"' + (st.cg ? '' : ' disabled') + '>Review</button>');
  }
  function profile(c) {
    return '<div class="ap-prof">' + av(c, true) + '<h3>' + c.n + '</h3><p class="ap-sub">' + c.yrs + ' &middot; lives near ' + c.town + '</p>' +
      '<p class="ap-quote">“' + c.hi + '”</p>' +
      '<p class="ap-lbl">Likes</p><div class="ap-tags">' + c.likes.map(function (l) { return '<span>' + l + '</span>'; }).join('') + '</div>' +
      '<ul class="ap-plan">' +
        '<li>' + ic('i-shield') + 'Fingerprint background check</li>' +
        '<li>' + ic('i-check') + 'Caring Companions orientation</li>' +
        (c.drives ? '<li>' + ic('i-car') + 'Can drive to outings and appointments</li>' : '') +
      '</ul><p class="ap-note">Sample profile for this preview.</p></div>' +
      foot('<button class="ap-btn ap-ghost" data-unview>Back</button><button class="ap-btn" data-cg="' + c.k + '" data-pickgo>Choose ' + c.n + '</button>');
  }
  function review() {
    var cost = st.hours * C.rate;
    var acts = C.activities.filter(function (a) { return st.acts.indexOf(a.k) > -1; });
    var cg = cgBy(st.cg);
    return head('Look good?') + '<div class="ap-card">' +
      (cg ? '<div class="ap-cg-line">' + av(cg) + '<span><b>' + cg.n + '</b><small>your caregiver</small></span></div>' : '<div class="ap-cg-line"><span class="ap-av" style="background:#8a96a3" aria-hidden="true">?</span><span><b>Best available caregiver</b><small>you’ll see their profile before the visit</small></span></div>') +
      '<p class="ap-when">' + DAYL[st.day.getDay()] + ', ' + MON[st.day.getMonth()] + ' ' + st.day.getDate() + '</p>' +
      '<p class="ap-time">' + hr(st.start) + ' to ' + hr(st.start + st.hours) + (st.repeat ? ' &middot; every week' : '') + '</p>' +
      '<ul class="ap-plan">' + acts.map(function (a) { return '<li>' + ic(a.i) + a.t + '</li>'; }).join('') + '</ul>' +
      '<div class="ap-cost"><span>' + C.rateLabel + ', ' + st.hours + ' hours at $' + C.rate + '</span><b>$' + cost + '</b></div></div>' +
      '<p class="ap-note">Nothing is charged in this preview.</p>' +
      foot('<button class="ap-btn ap-ghost" data-go="4">Back</button><button class="ap-btn" data-go="6">Book this visit</button>');
  }
  function booked() {
    return '<div class="ap-done"><div class="ap-tick" aria-hidden="true"><svg viewBox="0 0 52 52"><circle cx="26" cy="26" r="24"/><path d="M15 27l7 7 15-16"/></svg></div>' +
      '<h3>You’re all set.</h3><p>' + esc(st.who === 'Myself' ? 'Your' : st.who + '’s') + ' visit is on the calendar. ' + (cgBy(st.cg) ? cgBy(st.cg).n + ' will be there. You can message the office any time.' : 'We’ll send you your caregiver’s profile before the visit.') + '</p>' +
      '<div class="ap-list-preview on"><span>' + ic('i-calendar') + 'Upcoming visits</span><b>' + DAY[st.day.getDay()] + ' ' + MON[st.day.getMonth()] + ' ' + st.day.getDate() + ', ' + hr(st.start) + '</b></div>' +
      '<p class="ap-small">That’s how booking will work in our app. Want to be first in line?</p></div>' +
      foot('<a class="ap-btn" href="' + C.joinHref + '">' + C.joinLabel + '</a><button class="ap-btn ap-ghost" data-restart>Try again</button>');
  }

  function head(t) { return '<div class="ap-head"><span class="ap-step">Step ' + st.step + ' of ' + TOTAL + '</span><h3>' + t + '</h3><div class="ap-bar"><i style="width:' + (st.step / TOTAL * 100) + '%"></i></div></div>'; }
  function foot(btns) { return '<div class="ap-foot">' + btns + '</div>'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function render() {
    screen.innerHTML = STEPS[st.step]();
    screen.classList.remove('ap-in'); void screen.offsetWidth; screen.classList.add('ap-in');
    var sel = screen.querySelector('select[data-k="who"]'); if (sel) sel.value = st.who;
    var h = screen.querySelector('h3'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
  }

  function build() {
    root = document.createElement('div');
    root.className = 'ap-overlay';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-label', 'Preview of the ' + C.brand + ' booking app');
    root.innerHTML = '<div class="ap-wrap"><button class="ap-close" aria-label="Close preview">&times;</button>' +
      '<div class="ap-phone"><div class="ap-notch"></div><div class="ap-status"><span>9:41</span><span class="ap-sig" aria-hidden="true"><i></i><i></i><i></i></span></div>' +
      '<div class="ap-screen" aria-live="polite"></div></div>' +
      '<p class="ap-foot-note">' + C.footnote + '</p></div>';
    document.body.appendChild(root);
    screen = root.querySelector('.ap-screen');
    root.addEventListener('click', function (e) {
      if (e.target === root || e.target.closest('.ap-close')) return close();
      var t = e.target.closest('button, input, select'); if (!t) return;
      if (t.hasAttribute('data-view')) { st.view = t.getAttribute('data-view'); render(); return; }
      if (t.hasAttribute('data-unview')) { st.view = null; render(); return; }
      if (t.hasAttribute('data-cg')) { st.cg = t.getAttribute('data-cg'); st.view = null; if (t.hasAttribute('data-pickgo')) st.step = 5; render(); return; }
      if (t.hasAttribute('data-go')) { st.view = null; st.step = +t.getAttribute('data-go'); render(); return; }
      if (t.hasAttribute('data-restart')) { reset(); render(); return; }
      if (t.hasAttribute('data-day')) { st.day = days()[+t.getAttribute('data-day')]; render(); return; }
      if (t.hasAttribute('data-hours')) { st.hours = +t.getAttribute('data-hours'); if (st.start != null && st.start + st.hours > C.endHour) st.start = null; render(); return; }
      if (t.hasAttribute('data-start')) { st.start = +t.getAttribute('data-start'); render(); return; }
      if (t.hasAttribute('data-act')) { var k = t.getAttribute('data-act'), i = st.acts.indexOf(k); if (i > -1) st.acts.splice(i, 1); else st.acts.push(k); render(); return; }
    });
    root.addEventListener('change', function (e) {
      var k = e.target.getAttribute('data-k');
      if (k === 'who') st.who = e.target.value;
      if (k === 'repeat') st.repeat = e.target.checked;
    });
    document.addEventListener('keydown', function (e) {
      if (!root.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'Tab') { // keep focus inside the dialog
        var f = [].slice.call(root.querySelectorAll('button:not([disabled]), a[href], select, input'));
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
  }
  function open() {
    if (!root) build();
    lastFocus = document.activeElement;
    reset(); render();
    root.classList.add('open'); document.documentElement.classList.add('ap-lock');
    try { if (window.ccTrack) window.ccTrack('app_preview_open'); } catch (e) {}
  }
  function close() {
    root.classList.remove('open'); document.documentElement.classList.remove('ap-lock');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-app-preview]');
    if (t) { e.preventDefault(); open(); }
  });
  if (location.hash === '#app-preview') window.addEventListener('load', open);
})();
