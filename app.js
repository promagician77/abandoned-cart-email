(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var R = null, scen = 'missing_data', width = 600, tab = 'preview';
  var ORDER = ['one_item', 'three_items', 'nine_items', 'missing_data'];

  // tabs
  var tabs = [].slice.call(document.querySelectorAll('[role=tab]'));
  function show(id) {
    tab = id;
    tabs.forEach(function (t) { t.setAttribute('aria-selected', String(t.dataset.t === id)); });
    document.querySelectorAll('.panel').forEach(function (p) { p.hidden = p.id !== id; });
    document.querySelector('.bar').style.visibility = (id === 'preview' || id === 'ba') ? 'visible' : 'hidden';
    if (R) renderTab();
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { show(t.dataset.t); }); });

  // iframes size themselves to the email
  function fit(f) {
    try { var d = f.contentDocument; if (d && d.body) f.style.height = Math.max(400, d.documentElement.scrollHeight + 4) + 'px'; } catch (e) {}
  }
  ['f-main', 'f-naive', 'f-built'].forEach(function (id) {
    $(id).addEventListener('load', function () { fit($(id)); setTimeout(function () { fit($(id)); }, 300); });
  });
  function setWidth() { ['f-main', 'f-naive', 'f-built'].forEach(function (id) { $(id).style.width = width + 'px'; setTimeout(function () { fit($(id)); }, 320); }); }

  function renderPreview() {
    var s = R.scenarios[scen];
    if ($('f-main').dataset.src !== scen) { $('f-main').dataset.src = scen; $('f-main').src = 'render/' + scen + '.html'; }
    $('trig').innerHTML = s.triggers.map(function (t) { return '<li><b>' + esc(t[0]) + '</b><span>' + esc(t[1]) + '</span></li>'; }).join('');
    $('sizeline').innerHTML = 'Email size: <b>' + s.built_kb + ' KB</b> of Gmail\'s 102 KB limit. All ' + s.checks.length + ' QA checks pass.';
  }
  function renderBA() {
    var s = R.scenarios[scen];
    if ($('f-naive').dataset.src !== scen) { $('f-naive').dataset.src = scen; $('f-naive').src = 'render/' + scen + '_naive.html'; $('f-built').src = 'render/' + scen + '.html'; }
    $('ba-bad').textContent = s.naive_issues.length ? 'With this cart: ' + s.naive_issues.join(', ') + '. ' + s.naive_kb + ' KB.' : 'Looks fine with this cart, at ' + s.naive_kb + ' KB. Try "Missing data" or "9 items".';
    $('ba-good').textContent = 'Same data, same Klaviyo event: ' + s.built_kb + ' KB, every check passing.';
  }
  function renderSize() {
    var sw = R.sweep, W = 900, H = 360, L = 56, Rm = 20, T = 20, B = 44, maxY = 130;
    var x = function (n) { return L + (n - 1) * (W - L - Rm) / (sw.length - 1); };
    var y = function (v) { return T + (maxY - v) / maxY * (H - T - B); };
    var g = '';
    for (var v = 0; v <= maxY; v += 25) g += '<line x1="' + L + '" x2="' + (W - Rm) + '" y1="' + y(v) + '" y2="' + y(v) + '" stroke="#E4E8E6"/><text x="' + (L - 10) + '" y="' + (y(v) + 5) + '" text-anchor="end" font-size="13" fill="#59625F">' + v + ' KB</text>';
    sw.forEach(function (r) { if (r.items % 2 === 1 || r.items === 20) g += '<text x="' + x(r.items) + '" y="' + (H - 18) + '" text-anchor="middle" font-size="13" fill="#59625F">' + r.items + '</text>'; });
    g += '<text x="' + ((L + W - Rm) / 2) + '" y="' + (H - 1) + '" text-anchor="middle" font-size="13" fill="#59625F">items in the cart</text>';
    g += '<line x1="' + L + '" x2="' + (W - Rm) + '" y1="' + y(R.limit_kb) + '" y2="' + y(R.limit_kb) + '" stroke="#B4321F" stroke-width="2" stroke-dasharray="7 5"/><text x="' + (L + 8) + '" y="' + (y(R.limit_kb) - 8) + '" font-size="14" fill="#B4321F" font-weight="600">Gmail clips above 102 KB and hides the rest, including unsubscribe</text>';
    var path = function (k) { return sw.map(function (r, i) { return (i ? 'L' : 'M') + x(r.items).toFixed(1) + ' ' + y(r[k]).toFixed(1); }).join(' '); };
    g += '<path d="' + path('naive_kb') + '" fill="none" stroke="#B4321F" stroke-width="3"/><path d="' + path('built_kb') + '" fill="none" stroke="#0F766E" stroke-width="3"/>';
    var c = R.naive_clips_at_items, cr = sw[c - 1];
    if (cr) g += '<circle cx="' + x(c) + '" cy="' + y(cr.naive_kb) + '" r="6" fill="#B4321F"/><text x="' + (x(c) - 10) + '" y="' + (y(cr.naive_kb) + 42) + '" text-anchor="end" font-size="14" fill="#17201E">clipped at ' + c + ' items</text>';
    var last = sw[sw.length - 1];
    g += '<text x="' + (W - Rm) + '" y="' + (y(last.naive_kb) - 10) + '" text-anchor="end" font-size="14" fill="#B4321F" font-weight="600">Editor-style</text>';
    g += '<text x="' + (W - Rm) + '" y="' + (y(last.built_kb) - 10) + '" text-anchor="end" font-size="14" fill="#0F766E" font-weight="600">Built: ' + last.built_kb + ' KB at 20 items</text>';
    $('chart').innerHTML = g;
    $('size-sub').textContent = 'The editor-style template adds about ' + R.naive_kb_per_item + ' KB per product and gets clipped at ' + c + ' items. Mine shows three products and folds the rest into one line, so it stays under 7 KB however big the cart gets.';
  }
  var codeLoaded = false;
  function renderCode() {
    if (codeLoaded) return; codeLoaded = true;
    fetch('cart_module.txt').then(function (r) { return r.text(); }).then(function (t) {
      $('codeblock').dataset.raw = t;
      $('codeblock').innerHTML = esc(t).replace(/(\{%.*?%\})/g, '<span class="t">$1</span>').replace(/(\{\{.*?\}\})/g, '<span class="c">$1</span>');
    });
  }
  $('copy').addEventListener('click', function () {
    var t = $('codeblock').dataset.raw || ''; var b = $('copy');
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { b.textContent = 'Copied'; }, function () { b.textContent = 'Select and copy below'; });
    setTimeout(function () { b.textContent = 'Copy module'; }, 2000);
  });
  function renderQA() {
    var keys = ORDER, checks = R.scenarios[keys[0]].checks.map(function (c) { return c.check; });
    var h = '<thead><tr><th>Check</th>' + keys.map(function (k) { return '<th>' + esc(R.scenarios[k].label) + '</th>'; }).join('') + '</tr></thead><tbody>';
    checks.forEach(function (name, i) {
      h += '<tr><td>' + esc(name) + '</td>' + keys.map(function (k) {
        var c = R.scenarios[k].checks[i];
        return '<td class="r"><span class="' + (c.pass ? 'ok">Pass' : 'no">Fail') + '</span><small>' + esc(c.detail) + '</small></td>';
      }).join('') + '</tr>';
    });
    $('qatable').innerHTML = h + '</tbody>';
  }
  function renderTab() {
    if (tab === 'preview') renderPreview(); else if (tab === 'ba') renderBA();
    else if (tab === 'size') renderSize(); else if (tab === 'code') renderCode(); else if (tab === 'qa') renderQA();
  }

  // controls
  function seg(id, attr, onPick) {
    $(id).addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      $(id).querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-checked', String(x === b)); });
      onPick(b.dataset[attr]);
    });
  }
  seg('scenarios', 'k', function (k) { scen = k; renderTab(); });
  seg('devices', 'w', function (w) { width = +w; setWidth(); });

  fetch('report.json', { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (r) {
    R = r;
    $('scenarios').innerHTML = ORDER.map(function (k) { return '<button role="radio" aria-checked="' + (k === scen) + '" data-k="' + k + '">' + esc(r.scenarios[k].label) + '</button>'; }).join('');
    setWidth(); renderTab();
  }).catch(function () { $('trig').innerHTML = '<li><b>Could not load the test report</b><span>Refresh the page to try again.</span></li>'; });
})();
