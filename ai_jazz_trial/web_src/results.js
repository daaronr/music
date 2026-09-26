// Render /api/results for a browser that has voted; show the gate otherwise.
(function () {
  var NAMES = { halation: "Halation", parallax: "Parallax", glass_meridian: "Glass Meridian", none: "No preference" };
  var ORDER = ["halation", "parallax", "glass_meridian"];
  var voter = window.AJT_VOTER;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function barRow(label, value, max, numText, extraClass) {
    var row = el("div", "bar-row" + (extraClass ? " " + extraClass : ""));
    row.appendChild(el("span", "", label));
    var track = el("div", "bar-track");
    var fill = el("div", "bar-fill");
    fill.style.width = (max > 0 ? Math.round((value / max) * 100) : 0) + "%";
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(el("span", "bar-num", numText));
    return row;
  }
  function show(id) { document.getElementById(id).hidden = false; }

  function render(d) {
    var n = d.n;
    document.getElementById("res-n").textContent = n === 1
      ? "1 vote so far (yours)."
      : n + " votes so far, including yours.";
    var prefs = document.getElementById("prefs");
    ORDER.concat(["none"]).forEach(function (k) {
      var c = d.prefs[k] || 0;
      var pct = n ? Math.round((c / n) * 100) : 0;
      prefs.appendChild(barRow(NAMES[k], c, n, c + " (" + pct + "%)", k === "none" ? "none" : ""));
    });
    var ratings = document.getElementById("ratings");
    ORDER.forEach(function (k) {
      var r = d.ratings[k];
      var row = barRow(NAMES[k], r.mean || 0, 5, r.mean ? r.mean.toFixed(1) : "none");
      var label = row.firstChild;
      var dist = el("span", "dist");
      var peak = Math.max.apply(null, r.dist.concat([1]));
      r.dist.forEach(function (c, i) {
        var bar = el("i");
        bar.style.height = Math.round((c / peak) * 100) + "%";
        bar.title = (i + 1) + ": " + c + (c === 1 ? " vote" : " votes");
        dist.appendChild(bar);
      });
      label.appendChild(dist);
      label.appendChild(el("span", "opt", " n=" + r.n));
      ratings.appendChild(row);
    });
    var did = document.getElementById("did");
    var didNames = { listened: "Listened", read: "Read the sheets", played: "Played or sang" };
    Object.keys(didNames).forEach(function (k) {
      did.appendChild(barRow(didNames[k], d.did[k] || 0, n, String(d.did[k] || 0)));
    });
    var inst = d.instruments || [];
    document.getElementById("instruments").textContent = inst.length
      ? "Instruments mentioned: " + inst.map(function (p) { return p[0] + " (" + p[1] + ")"; }).join(", ") + "."
      : "No instruments mentioned yet.";
    show("res");
  }

  if (!voter) { show("gate"); return; }
  fetch("/api/results?voter=" + encodeURIComponent(voter), { cache: "no-store" })
    .then(function (r) { return r.json().then(function (j) { return { status: r.status, j: j }; }); })
    .then(function (res) {
      if (res.status === 403) { show("gate"); return; }
      if (res.status !== 200) throw new Error(res.j.error || "the results didn't load");
      render(res.j);
    })
    .catch(function (err) {
      document.getElementById("err-text").textContent = "Couldn't load the results (" + err.message + "). Try reloading in a moment.";
      show("err");
    });
})();
