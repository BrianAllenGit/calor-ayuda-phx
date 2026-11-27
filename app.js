(function () {
  'use strict';
  // Nothing is stored and nothing is sent. The language choice lives only in the page address (?lang=en).
  var TITLES = { es: 'Hace mucho calor: dónde refrescarte y cuándo pedir ayuda', en: 'It is very hot: where to cool off and when to get help' };
  var DESCS = {
    es: 'Dónde refrescarte en Phoenix, a quién llamar (211) y cuándo llamar al 911 por golpe de calor. Enlaces y textos oficiales, en español e inglés. Sin rastreo.',
    en: 'Where to cool off in Phoenix, who to call (211) and when to call 911 for heat stroke. Official links and texts, in Spanish and English. No tracking.'
  };
  var root = document.documentElement;

  function current() { return root.classList.contains('en') ? 'en' : 'es'; }

  function setLang(lang, keepHash) {
    if (lang !== 'en') lang = 'es';
    root.classList.toggle('en', lang === 'en');
    root.lang = lang;
    document.title = TITLES[lang];
    var md = document.querySelector('meta[name="description"]');
    if (md) md.setAttribute('content', DESCS[lang]);
    document.getElementById('lang-es').setAttribute('aria-pressed', String(lang === 'es'));
    document.getElementById('lang-en').setAttribute('aria-pressed', String(lang === 'en'));
    try {
      var hash = keepHash ? location.hash : '';
      history.replaceState(null, '', location.pathname + (lang === 'en' ? '?lang=en' : '') + hash);
    } catch (e) { /* file:// or old browser: the page still works */ }
  }

  function initial() {
    var m = /[?&]lang=(en|es)\b/.exec(location.search);
    if (m) return m[1];
    var h = /^#(en|es)-/.exec(location.hash);
    if (h) return h[1];
    return 'es'; // Spanish first
  }

  document.getElementById('lang-es').addEventListener('click', function () { setLang('es'); });
  document.getElementById('lang-en').addEventListener('click', function () { setLang('en'); });

  var printers = document.querySelectorAll('.js-print');
  for (var i = 0; i < printers.length; i++) printers[i].addEventListener('click', function () { window.print(); });

  // Move keyboard and screen reader focus to the section a menu button jumps to.
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var t = document.getElementById(a.getAttribute('href').slice(1));
    if (t && t.hasAttribute('tabindex')) setTimeout(function () { t.focus({ preventScroll: true }); }, 0);
  });

  setLang(initial(), true);
  if (location.hash && current() === 'en') {
    var el = document.getElementById(location.hash.slice(1));
    if (el) el.scrollIntoView();
  }
})();
