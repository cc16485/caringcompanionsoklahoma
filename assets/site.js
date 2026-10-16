// Caring Companions Oklahoma: menu toggle + contact form.
(function () {
  'use strict';
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Dropdown menus: open on click, close on outside click or Escape
  var groups = document.querySelectorAll('.nav-group');
  function closeAll(except) {
    groups.forEach(function (g) { if (g !== except) { g.classList.remove('open'); g.querySelector('.nav-top').setAttribute('aria-expanded', 'false'); } });
  }
  groups.forEach(function (g) {
    var b = g.querySelector('.nav-top');
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !g.classList.contains('open');
      closeAll(g);
      g.classList.toggle('open', open);
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.nav-group')) closeAll(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(); });

  var form = document.getElementById('lead-form');
  if (!form) return;
  var status = form.querySelector('.form-status');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = Object.fromEntries(new FormData(form).entries());
    if (d.website) return; // honeypot
    if (!d.name || !(d.phone || d.email)) {
      status.textContent = 'Please add your name and a phone number or email so we can reach you.';
      return;
    }
    var cfg = window.CC_FORM || {};
    if (!cfg.endpoint) {
      status.textContent = 'This form connects when the site opens. For now, please call us.';
      return;
    }
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true;
    status.textContent = 'Sending...';
    fetch(cfg.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: cfg.token, office: 'oklahoma', source: 'Website (Oklahoma)',
        name: d.name, phone: d.phone, email: d.email,
        note: ['Care for: ' + (d.client || ''), 'Town: ' + (d.town || ''), d.message || ''].join('\n')
      })
    }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      form.reset();
      status.textContent = 'Thank you. We have your message and will call you to find a time.';
    }).catch(function () {
      status.textContent = 'Sorry, that did not send. Please call us instead.';
    }).finally(function () { btn.disabled = false; });
  });
})();
