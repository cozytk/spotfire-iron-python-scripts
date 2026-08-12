(function () {
  "use strict";

  /* ---------- 테마 ---------- */
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("sf-theme"); } catch (e) {}
  if (!saved && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    saved = "dark";
  }
  if (saved) root.setAttribute("data-theme", saved);

  var themeBtn = document.getElementById("themeToggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("sf-theme", next); } catch (e) {}
    });
  }

  /* ---------- 모바일 목차 ---------- */
  var navBtn = document.getElementById("navToggle");
  var sidebar = document.getElementById("sidebar");
  if (navBtn && sidebar) {
    navBtn.addEventListener("click", function () { sidebar.classList.toggle("open"); });
  }

  /* ---------- 코드 복사 버튼 ---------- */
  document.querySelectorAll("div.codehilite").forEach(function (block) {
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "복사";
    btn.addEventListener("click", function () {
      var code = block.querySelector("code");
      var text = code ? code.innerText : "";
      var done = function () {
        btn.textContent = "복사됨";
        btn.classList.add("done");
        setTimeout(function () { btn.textContent = "복사"; btn.classList.remove("done"); }, 1500);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
    block.appendChild(btn);
  });

  /* ---------- 검색 ---------- */
  var input = document.getElementById("search");
  var panel = document.getElementById("searchResults");
  var index = null;

  function loadIndex() {
    if (index) return Promise.resolve(index);
    return fetch("search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; return index; })
      .catch(function () { index = []; return index; });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function snippet(body, q) {
    var i = body.toLowerCase().indexOf(q.toLowerCase());
    if (i < 0) return escapeHtml(body.slice(0, 110)) + "…";
    var start = Math.max(0, i - 45);
    var raw = body.slice(start, start + 150);
    var html = escapeHtml(raw);
    var re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig");
    return (start > 0 ? "…" : "") + html.replace(re, function (m) { return "<mark>" + m + "</mark>"; }) + "…";
  }

  function render(q) {
    if (!panel) return;
    if (!q || q.length < 2) { panel.hidden = true; return; }
    var lower = q.toLowerCase();
    var hits = index.filter(function (p) {
      return p.t.toLowerCase().indexOf(lower) >= 0 || p.b.toLowerCase().indexOf(lower) >= 0;
    }).slice(0, 12);

    if (!hits.length) {
      panel.innerHTML = '<p class="empty">"' + escapeHtml(q) + '" 검색 결과가 없습니다.</p>';
    } else {
      panel.innerHTML = hits.map(function (p) {
        return '<a href="' + p.u + '"><span class="st">' + escapeHtml(p.t) +
          '</span><span class="sb">' + snippet(p.b, q) + "</span></a>";
      }).join("");
    }
    panel.hidden = false;
  }

  if (input) {
    input.addEventListener("input", function () {
      var q = input.value.trim();
      loadIndex().then(function () { render(q); });
    });
    input.addEventListener("blur", function () {
      setTimeout(function () { if (panel) panel.hidden = true; }, 180);
    });
    input.addEventListener("focus", function () {
      if (input.value.trim().length >= 2) loadIndex().then(function () { render(input.value.trim()); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input) { e.preventDefault(); input.focus(); }
      if (e.key === "Escape" && panel) { panel.hidden = true; input.blur(); }
    });
  }

  /* ---------- 우측 목차 현재 위치 표시 ---------- */
  var links = Array.prototype.slice.call(document.querySelectorAll(".toc-side a"));
  if (links.length) {
    var targets = links.map(function (a) {
      return document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
    });
    var onScroll = function () {
      var pos = window.scrollY + 90, current = -1;
      targets.forEach(function (t, i) { if (t && t.offsetTop <= pos) current = i; });
      links.forEach(function (a, i) {
        a.style.color = i === current ? "var(--accent)" : "";
        a.style.fontWeight = i === current ? "600" : "";
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
})();
