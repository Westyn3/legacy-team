// The Legacy Team — small behaviours only: header state, mobile menu, lead routing.

(function () {
  // Header turns solid once the page is scrolled
  var header = document.querySelector('.site-header');
  function onScroll() { if (header) header.classList.toggle('solid', window.scrollY > 40); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var menu = document.getElementById('menu');
  var openBtn = document.getElementById('menu-open');
  var closeBtn = document.getElementById('menu-close');
  function setMenu(open) {
    if (!menu) return;
    menu.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    if (openBtn) openBtn.setAttribute('aria-expanded', String(open));
    if (open && closeBtn) closeBtn.focus();
    if (!open && openBtn) openBtn.focus();
  }
  if (openBtn) openBtn.addEventListener('click', function () { setMenu(true); });
  if (closeBtn) closeBtn.addEventListener('click', function () { setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu && menu.classList.contains('open')) setMenu(false); });

  // Contact form: route the lead to the agent who leads that market, then send without leaving the page.
  // Endpoints live on the <form> as data-karen / data-britney (set in site.yml).
  var form = document.getElementById('lead-form');
  if (form) {
    var status = document.getElementById('form-status');
    var interest = form.querySelector('[name="interest"]');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.dataset.preview) { status.textContent = 'This is a preview. The form sends on the live site.'; status.classList.add('show'); return; }
      var opt = interest ? interest.options[interest.selectedIndex] : null;
      var who = (opt && opt.dataset.agent) || 'karen';
      var endpoint = form.dataset[who] || form.getAttribute('action');
      var btn = form.querySelector('button[type="submit"]');
      var label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending';
      fetch(endpoint, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (res) {
          if (!res.ok) throw new Error('send failed');
          form.reset();
          status.textContent = 'Message sent. One of us will be in touch soon.';
          status.classList.add('show');
          btn.textContent = 'Sent';
        })
        .catch(function () {
          status.textContent = 'The message did not send. Please call or text (770) 316-0788, or email khilliard@kw.com.';
          status.classList.add('show');
          btn.disabled = false; btn.textContent = label;
        });
    });
  }
})();
