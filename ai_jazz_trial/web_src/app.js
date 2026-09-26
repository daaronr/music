// Voter id, shuffled order, tooltips, copy buttons and the vote form.
(function () {
  var TUNES = ["halation", "parallax", "glass_meridian"];

  function get(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  function newId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    return "v-" + Math.random().toString(36).slice(2) + "-" + Date.now().toString(36);
  }
  var voter = get("ajt_voter");
  if (!voter) { voter = newId(); set("ajt_voter", voter); }
  window.AJT_VOTER = voter;

  // one shuffled order per visitor, reused on every visit
  var order = null;
  try { order = JSON.parse(get("ajt_order") || "null"); } catch (e) { order = null; }
  if (!order || order.length !== TUNES.length) {
    order = TUNES.slice();
    for (var i = order.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = order[i]; order[i] = order[j]; order[j] = t;
    }
    set("ajt_order", JSON.stringify(order));
  }
  ["listen-grid", "pref-choices", "ratings"].forEach(function (id) {
    var box = document.getElementById(id);
    if (!box) return;
    order.forEach(function (k) {
      var el = box.querySelector('[data-tune="' + k + '"]');
      if (el) box.appendChild(el);
    });
    Array.prototype.forEach.call(box.querySelectorAll("[data-last]"), function (el) { box.appendChild(el); });
  });

  // tooltips: one floating box, kept inside the viewport
  var tip = document.getElementById("tooltip");
  function showTip(el) {
    if (!tip) return;
    tip.textContent = el.getAttribute("data-tip");
    tip.hidden = false;
    var r = el.getBoundingClientRect();
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
    var top = r.bottom + 8;
    if (top + h > window.innerHeight - 8) top = Math.max(8, r.top - h - 8);
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  }
  function hideTip() { if (tip) tip.hidden = true; }
  document.addEventListener("mouseover", function (e) {
    var el = e.target.closest && e.target.closest("[data-tip]");
    if (el) showTip(el);
  });
  document.addEventListener("mouseout", function (e) {
    if (e.target.closest && e.target.closest("[data-tip]")) hideTip();
  });
  document.addEventListener("focusin", function (e) {
    var el = e.target.closest && e.target.closest("[data-tip]");
    if (el) showTip(el); else hideTip();
  });
  document.addEventListener("focusout", hideTip);
  window.addEventListener("scroll", hideTip, { passive: true });

  var statusBox = document.getElementById("status"), statusTimer = null;
  function status(msg) {
    if (!statusBox) return;
    statusBox.textContent = msg; statusBox.hidden = false;
    clearTimeout(statusTimer);
    statusTimer = setTimeout(function () { statusBox.hidden = true; }, 5000);
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-tip]");
    if (el) { showTip(el); return; }
    hideTip();
    var copy = e.target.closest && e.target.closest("[data-copy]");
    if (copy) {
      var url = copy.getAttribute("data-copy");
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () {
          status("Copied. Paste it into Safari on a device with iReal Pro.");
        }, function () { window.prompt("Copy this iReal Pro link:", url); });
      } else { window.prompt("Copy this iReal Pro link:", url); }
    }
  });

  // vote form
  var form = document.getElementById("vote-form");
  if (!form) return;
  var msg = document.getElementById("vote-msg");
  var btn = document.getElementById("vote-btn");
  var votedBox = document.getElementById("voted");
  function showVoted(yes) { form.hidden = yes; votedBox.hidden = !yes; }
  if (get("ajt_voted") === "1") showVoted(true);
  document.getElementById("revote").addEventListener("click", function () { showVoted(false); });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var pref = form.querySelector('input[name="pref"]:checked');
    if (!pref) { msg.textContent = "Pick a favourite first (or “No preference”)."; return; }
    var ratings = {};
    TUNES.forEach(function (t) {
      var r = form.querySelector('input[name="r_' + t + '"]:checked');
      if (r) ratings[t] = Number(r.value);
    });
    var did = Array.prototype.map.call(form.querySelectorAll('input[name="did"]:checked'),
      function (x) { return x.value; });
    var body = { voter: voter, pref: pref.value, ratings: ratings, did: did,
      instrument: form.instrument.value, comment: form.comment.value };
    btn.disabled = true;
    msg.textContent = "Sending…";
    fetch("/api/vote", { method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.j.error || "Something went wrong.");
        set("ajt_voted", "1");
        msg.textContent = "";
        showVoted(true);
      })
      .catch(function (err) {
        msg.textContent = "Couldn't record your vote (" + err.message + "). Please try again in a moment.";
      })
      .then(function () { btn.disabled = false; });
  });
})();
