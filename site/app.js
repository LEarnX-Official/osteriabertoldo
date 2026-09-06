/* ===========================================================
   App logic — bilingual rendering, nav, booking, notice, and
   the whole animation layer. No 3D, no dependencies: every
   movement here is CSS driven from a handful of observers.
   =========================================================== */

const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

let lang = localStorage.getItem('bertoldo-lang')
        || (navigator.language || 'it').slice(0,2).toLowerCase();
if(!['it','en'].includes(lang)) lang = 'it';

const dig = (obj, path) => path.split('.').reduce((o,k) => o?.[k], obj);

/* ---------- render everything for a language ---------- */
function render(){
  const C = CONTENT[lang];
  document.documentElement.lang = lang;

  // simple data-t bindings
  $$('[data-t]').forEach(el => {
    const v = dig(C, el.dataset.t);
    if(typeof v === 'string') el.innerHTML = v;
  });

  // story paragraphs
  $('#storiaBody').innerHTML = C.storia.body.map(p => `<p>${p}</p>`).join('');
  $('#pillars').innerHTML = C.storia.pillars
    .map((p,i) => `<div class="pillar reveal d${i+1}"><b>${p.t}</b><span>${p.d}</span></div>`).join('');

  // dishes — each one owns a full-bleed cinematic band. The photograph
  // is inset and framed; a blurred blow-up of it fills the band behind,
  // so the small source image is never upscaled in focus.
  $('#dishHint').textContent = matchMedia('(hover:hover)').matches
    ? C.piatti.hint : C.piatti.hintTouch;
  $('#dishes').innerHTML = C.piatti.items.map((d,i) => `
    <article class="scene">
      <div class="scene-bg" style="background-image:url('${d.img}')"></div>
      <figure class="scene-plate" tabindex="0" role="button"
              aria-expanded="false" aria-label="${C.piatti.openLabel}: ${d.n}">
        <picture>
          <source srcset="${d.img.replace(/\.jpg$/,'.webp')}" type="image/webp">
          <img src="${d.img}" alt="${d.n}" width="535" height="535" loading="lazy">
        </picture>
        <div class="ingredients" aria-hidden="true">
          ${(d.ing||[]).map(g =>
            `<div class="ing">${iconSvg(g.icon)}<b>${g.n}</b><span>${g.d}</span></div>`).join('')}
          <p class="ing-note">${C.piatti.ingNote}</p>
        </div>
        <div class="shards" aria-hidden="true"></div>
        <svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48"/></svg>
        <span class="plate-cue">${C.piatti.open}</span>
      </figure>
      <div class="scene-copy">
        <span class="scene-no">${String(i+1).padStart(2,'0')}</span>
        <h3>${d.n}</h3>
        <hr class="rule">
        <p>${d.d}</p>
      </div>
    </article>`).join('');

  // menu — split sections across two columns
  const secs = C.menu.sections;
  const half = Math.ceil(secs.length/2);
  const col = arr => arr.map(s => `
    <div class="menu-sec">
      <h3>${s.name}</h3><hr class="rule">
      ${s.items.map(it => `
        <div class="m-item" data-diet="${it.diet||''}" data-gf="${it.gf?1:0}">
          <div class="m-text">
            <b>${it.n}${it.gf ? `<span class="m-gf">${C.menu.gf}</span>` : ''}</b>
            ${it.d ? `<span>${it.d}</span>` : ''}
          </div>
          <i class="m-dot"></i>
          <span class="m-price">${it.p}</span>
        </div>`).join('')}
    </div>`).join('');
  $('#menuCols').innerHTML =
    `<div class="reveal">${col(secs.slice(0,half))}</div>` +
    `<div class="reveal d2">${col(secs.slice(half))}</div>` +
    `<p class="menu-empty" id="menuEmpty" hidden>${C.menu.empty}</p>`;

  // dietary filter — the coeliac kitchen is a real selling point,
  // so it gets a control rather than a small tag
  const F = C.menu.filters;
  $('#menuFilter').setAttribute('aria-label', C.menu.filterLabel);
  $('#menuFilter').innerHTML = Object.keys(F).map(k =>
    `<button type="button" class="chip${k === menuFilter ? ' on' : ''}"
             data-filter="${k}" aria-pressed="${k === menuFilter}">${F[k]}</button>`).join('');

  // placeholder warning — honest about what is not real yet
  $('#menuNote').innerHTML =
    `<strong>${lang === 'it' ? 'Nota' : 'Note'}:</strong>&nbsp;${C.menu.note}`;

  applyMenuFilter();

  // reviews
  $('#reviews').innerHTML = C.recensioni.items.map((r,i) =>
    `<blockquote class="review reveal d${(i%2)+1}"><h3>${r.t}</h3><p>${r.q}</p></blockquote>`).join('');

  // running banner — the pillars, printed twice so the loop is seamless
  const words = C.storia.pillars.map(p => p.t);
  $('#marquee').innerHTML = [...words, ...words]
    .map(w => `<span>${w}</span>`).join('');

  // language buttons
  $('#langIt').setAttribute('aria-pressed', lang === 'it');
  $('#langEn').setAttribute('aria-pressed', lang === 'en');

  // notice
  paintNotice();

  // re-arm reveals and card tilt for freshly injected nodes
  armReveals();
  armTilt();
  sceneBgs = $$('.scene-bg');
  armShatter();
  kick();
}

/* ---------- menu dietary filter ---------- */
let menuFilter = localStorage.getItem('bertoldo-diet') || 'all';

function applyMenuFilter(){
  let shown = 0;
  $$('#menuCols .m-item').forEach(it => {
    const ok = menuFilter === 'all'
      || (menuFilter === 'gf'  && it.dataset.gf === '1')
      || it.dataset.diet === menuFilter;
    it.hidden = !ok;
    if(ok) shown++;
  });
  // a section whose items are all hidden should go too, or the page
  // fills with empty headings
  $$('#menuCols .menu-sec').forEach(sec => {
    sec.hidden = !sec.querySelector('.m-item:not([hidden])');
  });
  const msg = $('#menuEmpty');
  if(msg) msg.hidden = shown > 0;
}

document.addEventListener('click', e => {
  const chip = e.target.closest('#menuFilter .chip');
  if(!chip) return;
  menuFilter = chip.dataset.filter;
  localStorage.setItem('bertoldo-diet', menuFilter);
  $$('#menuFilter .chip').forEach(b => {
    const on = b === chip;
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
  applyMenuFilter();
});

/* ---------- scroll reveal (re-armable after re-render) ---------- */
let io;
function armReveals(){
  if(matchMedia('(prefers-reduced-motion: reduce)').matches){
    $$('.reveal').forEach(e => e.classList.add('in'));
    return;
  }
  io?.disconnect();
  io = new IntersectionObserver(es => {
    es.forEach(en => {
      if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, {threshold:.12, rootMargin:'0px 0px -8% 0px'});
  $$('.reveal, .wipe, .pillar, .sec-head, .scene').forEach(e => io.observe(e));
}

/* ---------- self-expiring notice ----------
   Replaces the old hard-coded popup that kept showing a date
   long after it had passed. */
function paintNotice(){
  const el = $('#notice');
  if(!NOTICE.active || new Date() > new Date(NOTICE.until + 'T23:59:59')){
    el.hidden = true; return;
  }
  if(sessionStorage.getItem('bertoldo-notice') === 'seen'){ el.hidden = true; return; }
  $('#noticeT').textContent = NOTICE[lang].title;
  $('#noticeB').textContent = NOTICE[lang].body;
  el.hidden = false;
  setTimeout(() => el.classList.add('show'), 1400);
}
$('#noticeX').addEventListener('click', () => {
  $('#notice').classList.remove('show');
  sessionStorage.setItem('bertoldo-notice','seen');
  setTimeout(() => { $('#notice').hidden = true; }, 600);
});

/* ---------- language switch ---------- */
function setLang(l){
  lang = l;
  localStorage.setItem('bertoldo-lang', l);
  render();
}
$('#langIt').addEventListener('click', () => setLang('it'));
$('#langEn').addEventListener('click', () => setLang('en'));

/* ---------- nav ---------- */
const nav = $('#nav');
addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', scrollY > 40);
}, {passive:true});

const burger = $('#burger'), links = $('#navLinks');
burger.addEventListener('click', () => {
  const open = links.classList.toggle('open');
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
});
links.addEventListener('click', e => {
  if(e.target.tagName === 'A'){
    links.classList.remove('open');
    burger.classList.remove('open');
    burger.setAttribute('aria-expanded','false');
  }
});

// active section highlighting
const secIds = ['home','storia','menu','galleria','contatti'];
const secObs = new IntersectionObserver(es => {
  es.forEach(en => {
    if(!en.isIntersecting) return;
    $$('.nav-links a').forEach(a =>
      a.classList.toggle('active', a.getAttribute('href') === '#' + en.target.id));
  });
}, {threshold:.35});
secIds.forEach(id => { const el = document.getElementById(id); if(el) secObs.observe(el); });

/* ---------- booking form ----------
   No backend here: it composes a pre-filled mailto so the request
   actually reaches the restaurant, which today takes bookings by
   phone and email only. Swap for a real endpoint when one exists. */
$('#bookForm').addEventListener('submit', e => {
  e.preventDefault();
  const f = e.target;
  if(!f.checkValidity()){
    $('#formMsg').textContent = lang === 'it'
      ? 'Controlla i campi obbligatori.' : 'Please check the required fields.';
    f.reportValidity(); return;
  }
  const v = id => document.getElementById(id).value.trim();
  const L = lang === 'it';
  const subject = L ? `Richiesta prenotazione — ${v('n')}` : `Booking request — ${v('n')}`;
  const body = [
    L ? `Data: ${v('d')}`     : `Date: ${v('d')}`,
    L ? `Orario: ${v('t')}`   : `Time: ${v('t')}`,
    L ? `Persone: ${v('p')}`  : `Guests: ${v('p')}`,
    L ? `Nome: ${v('n')}`     : `Name: ${v('n')}`,
    L ? `Telefono: ${v('ph')}`: `Phone: ${v('ph')}`,
    L ? `Email: ${v('em')}`   : `Email: ${v('em')}`,
    v('no') ? (L ? `Note: ${v('no')}` : `Notes: ${v('no')}`) : ''
  ].filter(Boolean).join('\n');

  location.href = `mailto:osteriabertoldo@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  $('#formMsg').textContent = L
    ? 'Apriamo il tuo client email con la richiesta compilata.'
    : 'Opening your email client with the request pre-filled.';
});

// don't let people book in the past
const dEl = $('#d');
dEl.min = new Date().toISOString().slice(0,10);
if(!dEl.value) dEl.value = dEl.min;

/* ===========================================================
   ANIMATION LAYER
   One rAF loop drives everything that tracks the pointer or the
   scroll position, so we never lay out on a scroll event.
   =========================================================== */
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = matchMedia('(hover:hover) and (pointer:fine)').matches;

const plate = $('#heroPlate');
let sceneBgs = [];
const bar   = $('#progress');
const lamp  = $('#lamp');

let pointerX = innerWidth/2, pointerY = innerHeight/2;   // target
let lampX = pointerX, lampY = pointerY;                  // eased
let ticking = false;

if(!calm && fine){
  addEventListener('pointermove', e => {
    pointerX = e.clientX; pointerY = e.clientY;
    document.body.classList.add('lamp-on');
    kick();
  }, {passive:true});
  addEventListener('pointerleave', () => document.body.classList.remove('lamp-on'));
}

addEventListener('scroll', kick, {passive:true});
addEventListener('resize', kick, {passive:true});

function kick(){
  if(ticking) return;
  ticking = true;
  requestAnimationFrame(frame);
}

function frame(){
  const y   = scrollY;
  const max = document.documentElement.scrollHeight - innerHeight;

  // scroll progress rail
  bar.style.transform = `scaleX(${max > 0 ? Math.min(y/max,1) : 0})`;

  // hero parallax: the photographic plate drifts slower than the page,
  // and leans a little toward the pointer
  if(plate && !calm){
    const inHero = y < innerHeight;
    if(inHero){
      const tiltX = fine ? (pointerX/innerWidth  - .5) * 22 : 0;
      const tiltY = fine ? (pointerY/innerHeight - .5) * 14 : 0;
      plate.style.transform =
        `scale(1.06) translate3d(${tiltX}px, ${y * .22 - tiltY}px, 0)`;
    }
  }

  // each visible scene's blurred backdrop drifts against the page,
  // which is what makes the bands feel like moving sets rather than blocks
  if(!calm){
    for(const bg of sceneBgs){
      const band = bg.parentElement.getBoundingClientRect();
      if(band.bottom < -200 || band.top > innerHeight + 200) continue;
      const p = (band.top + band.height/2 - innerHeight/2) / innerHeight;
      bg.style.transform = `scale(1.15) translate3d(0,${(-p * 60).toFixed(1)}px,0)`;
    }
  }

  // warm lamp trails the cursor with a little inertia
  if(!calm && fine){
    lampX += (pointerX - lampX) * .09;
    lampY += (pointerY - lampY) * .09;
    lamp.style.transform = `translate3d(${lampX}px, ${lampY}px, 0)`;
    // keep easing while the lamp is still catching up
    if(Math.hypot(pointerX-lampX, pointerY-lampY) > .5){
      requestAnimationFrame(frame); return;
    }
  }
  ticking = false;
}

/* nav hides going down, returns coming up — more room for the page */
let lastY = 0;
addEventListener('scroll', () => {
  const y = scrollY;
  nav.classList.toggle('hide', y > lastY && y > 420 && !links.classList.contains('open'));
  lastY = y;
}, {passive:true});

/* buttons lean toward the cursor */
if(!calm && fine){
  $$('.btn').forEach(b => {
    b.addEventListener('pointermove', e => {
      const r = b.getBoundingClientRect();
      b.style.transform =
        `translate(${(e.clientX - r.left - r.width/2) * .16}px,
                   ${(e.clientY - r.top - r.height/2) * .22 - 3}px)`;
    });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });
}

/* the framed plate leans toward the pointer inside its band */
function armTilt(){
  if(calm || !fine) return;
  $$('.scene').forEach(scene => {
    const plate = scene.querySelector('.scene-plate');
    if(!plate) return;
    scene.addEventListener('pointermove', e => {
      if(scene.classList.contains('broken')) return;   // hold still while open
      const r = scene.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width  - .5;
      const py = (e.clientY - r.top)  / r.height - .5;
      plate.style.transform =
        `perspective(1100px) rotateX(${-py*4}deg) rotateY(${px*5}deg) translateY(-6px)`;
    });
    scene.addEventListener('pointerleave', () => { plate.style.transform = ''; });
  });
}

/* ---------- the shatter ----------
   Shards are built lazily the first time a plate is opened, so six plates
   do not cost 6xN nodes up front. Each shard is a slice of the same photo,
   positioned by background-position so they reassemble the image exactly. */
const SHARD_COLS = 7, SHARD_ROWS = 7;

function buildShards(plate){
  const box = plate.querySelector('.shards');
  if(box.childElementCount) return;                 // already built
  const src = plate.querySelector('img').currentSrc || plate.querySelector('img').src;
  const w = 100 / SHARD_COLS, h = 100 / SHARD_ROWS;
  const frag = document.createDocumentFragment();

  for(let r = 0; r < SHARD_ROWS; r++){
    for(let c = 0; c < SHARD_COLS; c++){
      const sh = document.createElement('i');
      sh.className = 'shard';
      sh.style.cssText =
        `left:${c*w}%;top:${r*h}%;width:${w}%;height:${h}%;` +
        `background-image:url("${src}");background-size:${SHARD_COLS*100}% ${SHARD_ROWS*100}%;` +
        `background-position:${(c/(SHARD_COLS-1))*100}% ${(r/(SHARD_ROWS-1))*100}%;`;
      // where this shard flies: outward from the centre and toward the
      // viewer in z, tumbling on all three axes. The centre shards come
      // furthest forward, so the plate appears to burst open.
      const dx = (c + .5)/SHARD_COLS - .5, dy = (r + .5)/SHARD_ROWS - .5;
      const radial = Math.hypot(dx, dy);
      const dist = 150 + Math.random()*180;
      sh.dataset.tx = (dx * dist).toFixed(1);
      sh.dataset.ty = (dy * dist - 18).toFixed(1);
      sh.dataset.tz = (150 + (1 - radial*2) * 190 + Math.random()*90).toFixed(0);
      sh.dataset.rx = ((Math.random() - .5) * 190).toFixed(0);
      sh.dataset.ry = ((Math.random() - .5) * 190).toFixed(0);
      sh.dataset.rz = ((Math.random() - .5) * 150).toFixed(0);
      sh.style.transitionDelay = (radial * 300).toFixed(0) + 'ms';
      frag.appendChild(sh);
    }
  }
  box.appendChild(frag);
}

function toggleShatter(scene){
  const plate = scene.querySelector('.scene-plate');
  const open  = !scene.classList.contains('broken');

  if(open){
    buildShards(plate);
    // force a reflow so the shards are painted at rest before we move them;
    // rAF would be throttled in a background tab and strand them mid-flight
    void plate.offsetHeight;
    scene.classList.add('broken');
    plate.setAttribute('aria-expanded','true');
    plate.querySelector('.ingredients').setAttribute('aria-hidden','false');
    for(const sh of plate.querySelectorAll('.shard')){
      sh.style.transform =
        `translate3d(${sh.dataset.tx}%, ${sh.dataset.ty}%, ${sh.dataset.tz}px)` +
        ` rotateX(${sh.dataset.rx}deg) rotateY(${sh.dataset.ry}deg) rotateZ(${sh.dataset.rz}deg)`;
    }
  }else{
    scene.classList.remove('broken');
    plate.setAttribute('aria-expanded','false');
    plate.querySelector('.ingredients').setAttribute('aria-hidden','true');
    for(const sh of plate.querySelectorAll('.shard')) sh.style.transform = '';
  }
}

function armShatter(){
  $$('.scene').forEach(scene => {
    const plate = scene.querySelector('.scene-plate');
    if(!plate || plate.dataset.armed) return;
    plate.dataset.armed = '1';
    plate.addEventListener('click', () => toggleShatter(scene));
    plate.addEventListener('keydown', e => {
      if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); toggleShatter(scene); }
    });
  });
}

/* ---------- boot ---------- */
$('#yr').textContent = new Date().getFullYear();
render();
kick();

// hold the loader just long enough for the monogram to finish drawing,
// then let the hero copy rise. Never gate the copy on `load` alone —
// if that has already fired the listener would never run and the hero
// would stay blank, so we always arm a timer as well.
const loader = $('#loader');
let lifted = false;
function lift(){
  if(lifted) return;
  lifted = true;
  loader.classList.add('done');
  document.body.classList.add('ready');
  setTimeout(() => { loader.style.display = 'none'; }, 700);
}
if(calm){
  lift();
}else{
  const hold = 1500;
  if(document.readyState === 'complete') setTimeout(lift, hold);
  else addEventListener('load', () => setTimeout(lift, hold));
  setTimeout(lift, 3800);          // hard ceiling: a slow image never blocks the copy
}
