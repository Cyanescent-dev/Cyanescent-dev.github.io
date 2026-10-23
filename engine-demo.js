/* ═══════════════════════════════════════════════════════════════
   Cyanescent Player 1.0 — "Inside the analysis" readout
   A deterministic model of a 64-bar, 145 BPM psytrance track,
   drawn as the lanes the Player's analysis produces, with the
   per-frame signals presets receive at the playhead. Values are
   illustrative; the structure mirrors the real engine.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var root = document.querySelector('[data-engine]');
  if (!root) return;

  var svg = root.querySelector('[data-engine-svg]');
  var scrub = root.querySelector('[data-engine-scrub]');
  var playBtn = root.querySelector('[data-engine-play]');
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var NS = 'http://www.w3.org/2000/svg';

  /* ─── Track model ─── */

  var BPM = 145;
  var BEATS = 256;
  var SECONDS_PER_BEAT = 60 / BPM;

  var SECTIONS = [
    { start: 0, end: 32, name: 'Intro', energy: 1, role: 'Calm', kick: false },
    { start: 32, end: 64, name: 'Groove', energy: 3, role: 'High energy', kick: true },
    { start: 64, end: 96, name: 'Build', energy: 4, role: 'Build', kick: true, riser: true, breakFrom: 88 },
    { start: 96, end: 160, name: 'Drop', energy: 5, role: 'Drop', kick: true },
    { start: 160, end: 192, name: 'Breakdown', energy: 2, role: 'Breakdown', kick: false },
    { start: 192, end: 224, name: 'Build', energy: 4, role: 'Build', kick: true, riser: true, breakFrom: 216 },
    { start: 224, end: 256, name: 'Drop', energy: 5, role: 'Drop', kick: true }
  ];
  var DROPS = [96, 224];
  var FILL = { start: 52, end: 54 };
  var TRANSITIONS = [64, 96, 160, 224];
  var LOOKAHEAD = [
    { seconds: 0.5, beats: 0.5 / SECONDS_PER_BEAT },
    { seconds: 5, beats: 5 / SECONDS_PER_BEAT },
    { seconds: 20, beats: 20 / SECONDS_PER_BEAT }
  ];

  function sectionAt(b) {
    for (var i = 0; i < SECTIONS.length; i++) {
      if (b < SECTIONS[i].end) return SECTIONS[i];
    }
    return SECTIONS[SECTIONS.length - 1];
  }

  function noise(x) {
    var s = Math.sin(x * 12.9898 + 78.233) * 43758.5453;
    return s - Math.floor(s);
  }

  function inBreak(sec, b) {
    return sec.breakFrom !== undefined && b >= sec.breakFrom;
  }

  function inFill(b) {
    return b >= FILL.start && b < FILL.end;
  }

  function kickOn(b) {
    var sec = sectionAt(b);
    return sec.kick && !inBreak(sec, b) && !inFill(b);
  }

  function kick(b) {
    return kickOn(b) ? Math.exp(-(b % 1) * 7) : 0;
  }

  function low(b) {
    var sec = sectionAt(b);
    var base = { Intro: 0.14, Groove: 0.72, Build: 0.74, Drop: 0.95, Breakdown: 0.1 }[sec.name];
    if (inBreak(sec, b)) base = 0.07;
    if (inFill(b)) base = 0.18;
    return Math.min(1, base * (kickOn(b) ? 0.55 + 0.45 * kick(b) : 1) + noise(b * 7) * 0.04);
  }

  function rampIn(sec, b) {
    return (b - sec.start) / (sec.end - sec.start);
  }

  function mid(b) {
    var sec = sectionAt(b);
    var base = { Intro: 0.28, Groove: 0.5, Build: 0.52 + 0.2 * rampIn(sec, b), Drop: 0.76, Breakdown: 0.58 }[sec.name];
    return Math.min(1, base + (noise(b * 3.1) - 0.5) * 0.12);
  }

  function high(b) {
    var sec = sectionAt(b);
    var base = sec.riser
      ? 0.36 + 0.6 * Math.pow(rampIn(sec, b), 1.6)
      : { Intro: 0.18, Groove: 0.44, Drop: 0.72, Breakdown: 0.34 }[sec.name];
    return Math.min(1, base + (noise(b * 5.7) - 0.5) * 0.1);
  }

  function energy(b) {
    return Math.min(1, low(Math.floor(b) + 0.15) * 0.45 + mid(b) * 0.3 + high(b) * 0.25);
  }

  function futureEnergy(b) {
    var ahead = LOOKAHEAD[2].beats;
    var sum = 0;
    for (var i = 0; i < 8; i++) sum += energy(Math.min(BEATS - 0.5, b + ahead * (i + 1) / 8));
    return sum / 8;
  }

  function nextDrop(b) {
    for (var i = 0; i < DROPS.length; i++) if (DROPS[i] > b) return DROPS[i];
    return null;
  }

  function upcomingDrop(b) {
    var d = nextDrop(b);
    if (d === null) return 0;
    var x = 1 - Math.min(1, (d - b) / 32);
    return x * x * (3 - 2 * x);
  }

  function role(b) {
    var sec = sectionAt(b);
    if (sec.name === 'Drop' && b - sec.start >= 32) return 'High energy';
    return sec.role;
  }

  /* ─── Drawing ─── */

  var X0 = 118;
  var X1 = 990;
  var LANES = {
    ruler: [8, 34],
    wave: [42, 108],
    bands: [118, 214],
    energy: [226, 254],
    drops: [266, 314],
    adaptive: [326, 368]
  };

  function x(b) {
    return X0 + (b / BEATS) * (X1 - X0);
  }

  function el(name, attrs, parent) {
    var node = document.createElementNS(NS, name);
    for (var k in attrs) node.setAttribute(k, attrs[k]);
    (parent || svg).appendChild(node);
    return node;
  }

  function text(str, attrs, parent) {
    var node = el('text', attrs, parent);
    node.textContent = str;
    return node;
  }

  function draw() {
    var defs = el('defs', {});
    var g1 = el('linearGradient', { id: 'eg-lead', x1: '0', x2: '1' }, defs);
    el('stop', { offset: '0', 'stop-color': '#ff5bd6', 'stop-opacity': '0' }, g1);
    el('stop', { offset: '1', 'stop-color': '#ff5bd6', 'stop-opacity': '0.55' }, g1);
    var g2 = el('linearGradient', { id: 'eg-wave', gradientUnits: 'userSpaceOnUse', x1: X0, x2: X1, y1: 0, y2: 0 }, defs);
    el('stop', { offset: '0', 'stop-color': '#5ef0ff' }, g2);
    el('stop', { offset: '0.5', 'stop-color': '#9b7bff' }, g2);
    el('stop', { offset: '1', 'stop-color': '#ff5bd6' }, g2);

    // lane labels
    var labels = [
      ['Beat grid', LANES.ruler, 'bars · phrases'],
      ['Waveform', LANES.wave, ''],
      ['Bands', LANES.bands, 'low · mid · high'],
      ['Energy', LANES.energy, 'sections 1–5'],
      ['Drop map', LANES.drops, 'lead-in → drop'],
      ['Adaptive', LANES.adaptive, 'transitions']
    ];
    labels.forEach(function (l) {
      var mid = (l[1][0] + l[1][1]) / 2;
      text(l[0], { x: 8, y: mid - (l[2] ? 3 : -4), class: 'eg-lane' });
      if (l[2]) text(l[2], { x: 8, y: mid + 11, class: 'eg-sub' });
    });

    // grid: beats, bars, 8-beat phrases, 32-beat phrases
    var grid = el('g', { class: 'eg-grid' });
    for (var b = 0; b <= BEATS; b += 4) {
      var cls = b % 32 === 0 ? 'eg-g32' : b % 8 === 0 ? 'eg-g8' : 'eg-g4';
      var top = b % 32 === 0 ? LANES.ruler[0] + 12 : b % 8 === 0 ? LANES.ruler[1] - 10 : LANES.ruler[1] - 5;
      el('line', { x1: x(b), x2: x(b), y1: top, y2: b % 8 === 0 ? LANES.adaptive[1] : LANES.ruler[1], class: cls }, grid);
      if (b % 32 === 0 && b < BEATS) text('bar ' + (b / 4 + 1), { x: x(b) + 3, y: LANES.ruler[0] + 9, class: 'eg-tick' }, grid);
    }

    // waveform: mirrored bars every half beat
    var wave = el('g', { fill: 'url(#eg-wave)' });
    var wc = (LANES.wave[0] + LANES.wave[1]) / 2;
    var wh = (LANES.wave[1] - LANES.wave[0]) / 2;
    var step = 0.5;
    var w = (x(step) - x(0)) * 0.72;
    for (var t = 0; t < BEATS; t += step) {
      var e = Math.pow(energy(t + 0.05), 1.5);
      var amp = Math.max(0.05, Math.min(1, (0.1 + 0.95 * e) * (kickOn(t) ? 0.6 + 0.4 * kick(t + 0.05) : 0.7) + (noise(t * 9) - 0.5) * 0.1));
      el('rect', { x: x(t), y: wc - amp * wh, width: w, height: amp * wh * 2, rx: 0.6 }, wave);
    }

    // bands as stacked area lines
    var bands = [
      { fn: low, cls: 'eg-low' },
      { fn: mid, cls: 'eg-mid' },
      { fn: high, cls: 'eg-high' }
    ];
    var bh = LANES.bands[1] - LANES.bands[0];
    bands.forEach(function (band, i) {
      var y0 = LANES.bands[0] + (bh / 3) * (i + 1) - 2;
      var hh = bh / 3 - 6;
      var d = 'M' + x(0) + ' ' + y0;
      for (var b = 0; b <= BEATS; b += 0.5) d += ' L' + x(b).toFixed(1) + ' ' + (y0 - band.fn(Math.min(b, BEATS - 0.5)) * hh).toFixed(1);
      d += ' L' + x(BEATS) + ' ' + y0 + ' Z';
      el('path', { d: d, class: band.cls });
    });
    text('low < 180 Hz · kick', { x: x(1), y: LANES.bands[0] + 9, class: 'eg-inline' });
    text('mid', { x: x(1), y: LANES.bands[0] + bh / 3 + 9, class: 'eg-inline' });
    text('high > 2.4 kHz · riser', { x: x(1), y: LANES.bands[0] + (bh * 2) / 3 + 9, class: 'eg-inline' });

    // energy sections
    SECTIONS.forEach(function (sec) {
      el('rect', {
        x: x(sec.start) + 1, y: LANES.energy[0], width: x(sec.end) - x(sec.start) - 2,
        height: LANES.energy[1] - LANES.energy[0], rx: 4, class: 'eg-e' + sec.energy
      });
      text(sec.name + ' · ' + sec.energy, { x: x(sec.start) + 6, y: LANES.energy[1] - 9, class: 'eg-sec' });
    });

    // drop map: lead-in ramps and markers; the fill that is not a drop
    var dTop = LANES.drops[0] + 10;
    var dBot = LANES.drops[1];
    DROPS.forEach(function (db) {
      el('path', { d: 'M' + x(db - 32) + ' ' + dBot + ' L' + x(db) + ' ' + dTop + ' L' + x(db) + ' ' + dBot + ' Z', fill: 'url(#eg-lead)' });
      el('line', { x1: x(db), x2: x(db), y1: dTop - 6, y2: dBot, class: 'eg-drop' });
      el('circle', { cx: x(db), cy: dTop - 6, r: 4, class: 'eg-drop-dot' });
      text('major drop', { x: x(db) + 6, y: dTop, class: 'eg-drop-label' });
    });
    el('line', { x1: x(FILL.start), x2: x(FILL.start), y1: dTop + 12, y2: dBot, class: 'eg-fill' });
    text('fill, not a drop', { x: x(FILL.start) + 5, y: dTop + 22, class: 'eg-fill-label' });

    // adaptive transitions landing on phrase boundaries
    var ay = (LANES.adaptive[0] + LANES.adaptive[1]) / 2;
    TRANSITIONS.forEach(function (tb, i) {
      el('path', { d: 'M' + x(tb) + ' ' + (ay - 7) + ' l7 7 l-7 7 l-7 -7 Z', class: 'eg-trans' });
      if (i === 0) text('phrase boundary', { x: x(tb) + 10, y: ay + 4, class: 'eg-trans-label' });
      if (i === 1) text('on the drop', { x: x(tb) + 10, y: ay + 4, class: 'eg-trans-label' });
    });

    // playhead with lookahead windows
    var ph = el('g', { 'data-playhead': '' });
    for (var i = LOOKAHEAD.length - 1; i >= 0; i--) {
      el('rect', {
        x: 0, y: LANES.wave[0] - 4, width: x(LOOKAHEAD[i].beats) - x(0),
        height: LANES.drops[1] - LANES.wave[0] + 4, class: 'eg-look eg-look' + i, 'data-look': i
      }, ph);
    }
    text('lookahead 0.5 s · 5 s · 20 s', { x: 6, y: LANES.ruler[1] - 2, class: 'eg-look-label' }, ph);
    el('line', { x1: 0, x2: 0, y1: LANES.ruler[0], y2: LANES.adaptive[1], class: 'eg-playhead' }, ph);
    el('circle', { cx: 0, cy: LANES.ruler[0], r: 4.5, class: 'eg-playhead-dot' }, ph);
    return ph;
  }

  var playhead = draw();

  /* ─── Signals panel ─── */

  var bars = {};
  root.querySelectorAll('[data-bar]').forEach(function (n) { bars[n.getAttribute('data-bar')] = n; });
  var sig = {};
  root.querySelectorAll('[data-sig]').forEach(function (n) { sig[n.getAttribute('data-sig')] = n; });
  var dots = sig.beatdots ? sig.beatdots.querySelectorAll('i') : [];
  var lastRole = '';

  function setBar(name, v) {
    if (bars[name]) bars[name].style.transform = 'scaleX(' + Math.max(0, Math.min(1, v)).toFixed(3) + ')';
  }

  function render(b) {
    b = Math.max(0, Math.min(BEATS - 0.01, b));
    playhead.setAttribute('transform', 'translate(' + x(b).toFixed(2) + ' 0)');

    var beatInBar = Math.floor(b) % 4;
    for (var i = 0; i < dots.length; i++) dots[i].classList.toggle('on', i === beatInBar);
    var bar = Math.floor(b / 4) + 1;
    var phrase = Math.floor(b / 32) + 1;
    sig.bar.textContent = 'bar ' + bar + ' · phrase ' + phrase + ' of 8';
    setBar('phrase', (b % 32) / 32);
    setBar('low', low(b));
    setBar('mid', mid(b));
    setBar('high', high(b));
    setBar('kick', kick(b));
    setBar('energy', energy(b));
    setBar('future', futureEnergy(b));
    setBar('upcoming', upcomingDrop(b));

    var d = nextDrop(b);
    var sinceDrop = DROPS.filter(function (db) { return db <= b; }).map(function (db) { return b - db; }).pop();
    sig.drop.textContent = sinceDrop !== undefined && sinceDrop < 4 ? 'drop now' : d === null ? 'no more drops' : 'in ' + Math.ceil(d - b) + ' beats';
    var r = role(b);
    if (r !== lastRole) {
      sig.role.textContent = r;
      sig.role.setAttribute('data-role', r.toLowerCase().replace(/\s+/g, '-'));
      lastRole = r;
    }
  }

  /* ─── Playback ─── */

  var position = parseFloat(scrub.value) || 92;
  var playing = false;
  var visible = false;
  var last = 0;

  function frame(now) {
    if (!playing || !visible) { last = 0; return; }
    if (last) {
      position += (now - last) / 1000 / SECONDS_PER_BEAT;
      if (position >= BEATS) position = 0;
      scrub.value = position;
      render(position);
    }
    last = now;
    requestAnimationFrame(frame);
  }

  function setPlaying(on) {
    playing = on;
    playBtn.textContent = on ? 'Pause' : 'Play';
    playBtn.setAttribute('aria-pressed', String(on));
    if (on) { last = 0; requestAnimationFrame(frame); }
  }

  playBtn.addEventListener('click', function () { setPlaying(!playing); });

  scrub.addEventListener('input', function () {
    position = parseFloat(scrub.value);
    render(position);
  });

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible && playing) { last = 0; requestAnimationFrame(frame); }
    }, { threshold: 0.15 }).observe(root);
  } else {
    visible = true;
  }

  render(position);
  // Autoplay only when motion is welcome; the Pause button stays available.
  if (!reducedMotion.matches) setPlaying(true);
})();
