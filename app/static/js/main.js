// ── NAVBAR SCROLL ────────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar')
    .classList.toggle('scrolled', window.scrollY > 50);
});

// ── SEARCH ───────────────────────────────────────────────────────────────────
function toggleSearch() {
  const inp = document.getElementById('searchInput');
  inp.classList.toggle('open');
  if (inp.classList.contains('open')) inp.focus();
}

function doSearch() {
  const q = document.getElementById('searchInput').value.trim();
  if (q) window.location = '/search?q=' + encodeURIComponent(q);
}

// ── TOGGLE SENHA ─────────────────────────────────────────────────────────────
function togglePw(id) {
  const el = document.getElementById(id);
  el.type = el.type === 'password' ? 'text' : 'password';
}

// ── FLASH AUTO-DISMISS ───────────────────────────────────────────────────────
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity .5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 4000);

// ── YOUTUBE THUMBNAIL FALLBACK ───────────────────────────────────────────────
var _ytFallbacks = ['mqdefault', 'sddefault', 'default'];
function ytFallback(img, id) {
  var tried = img.dataset.ytTried ? parseInt(img.dataset.ytTried) : 0;
  if (tried < _ytFallbacks.length) {
    img.dataset.ytTried = tried + 1;
    img.src = 'https://img.youtube.com/vi/' + id + '/' + _ytFallbacks[tried] + '.jpg';
  } else {
    img.onerror = null;
  }
}

// ── COUNTDOWN (cadastro por e-mail) ──────────────────────────────────────────
function startCountdown(seconds, elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  let rem = seconds;
  const iv = setInterval(() => {
    rem--;
    const m = String(Math.floor(rem / 60)).padStart(1, '0');
    const s = String(rem % 60).padStart(2, '0');
    el.textContent = `${m}:${s}`;
    if (rem <= 0) {
      clearInterval(iv);
      el.textContent = 'Expirado';
      el.style.color = '#777';
    }
  }, 1000);
}
