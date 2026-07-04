/* Disco del Giorno - elenco lato client. Nessun build step.
   Dati da data/albums.js (window.ALBUMS) e data/covers.js (window.COVERS). */
(function () {
  "use strict";

  var ALBUMS = (window.ALBUMS || []).slice();
  var COVERS = window.COVERS || {};
  var POPULARITY = window.POPULARITY || {};
  var SVGNS = "http://www.w3.org/2000/svg";

  function fold(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function decadeOf(year) {
    return year ? Math.floor(year / 10) * 10 : null;
  }
  function $(id) { return document.getElementById(id); }

  // Etichetta "Artista - Titolo" usata in piu' punti (link, aria-label, disco del giorno).
  function albumLabel(a) {
    return (a.artist ? a.artist + " - " : "") + a.album;
  }

  /* ---- servizi: logo del brand + URL di ricerca ---- */
  var ICON = {
    spotify: ["M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"],
    youtube: ["M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"],
    amazon: [
      "M3 15.6c2.6 2 5.9 3 9.1 3 2.2 0 4.7-.5 6.8-1.6.32-.16.58.2.28.42-2 1.6-5 2.4-7.6 2.4-3.6 0-7-1.4-9.6-3.8-.2-.2.06-.5.34-.62z",
      "M20.7 14.7c-.34-.43-2.05-.2-2.82-.1-.2.02-.24-.16-.04-.3.9-.62 2.38-.44 2.55-.23.18.2-.05 1.7-.66 2.4-.1.12-.27.06-.22-.1.16-.5.42-1.34.27-1.67z"
    ],
    rym: ["M12 2l2.9 6.3 6.9.6-5.2 4.5 1.6 6.7L12 17.3 5.8 20.6l1.6-6.7L2.2 8.9l6.9-.6L12 2z"],
    discogs: ["M1.7422 11.982c0-5.6682 4.61-10.2782 10.2758-10.2782 1.8238 0 3.5372.48 5.0251 1.3175l.8135-1.4879C16.1768.588 14.2474.036 12.1908.0024h-.1944C5.4091.0144.072 5.3107 0 11.886v.1152c.0072 3.4389 1.4567 6.5345 3.7748 8.7207l1.1855-1.2814c-1.9798-1.8743-3.218-4.526-3.218-7.4585zM20.362 3.4053l-1.1543 1.2406c1.903 1.867 3.0885 4.4636 3.0885 7.3361 0 5.6658-4.61 10.2758-10.2758 10.2758-1.783 0-3.4605-.456-4.922-1.2575l-.8542 1.5214c1.7086.9384 3.6692 1.4735 5.7546 1.4759C18.6245 23.9976 24 18.6246 24 11.9988c-.0048-3.3717-1.399-6.4146-3.638-8.5935zM1.963 11.982c0 2.8701 1.2119 5.4619 3.146 7.2953l1.1808-1.2767c-1.591-1.5166-2.587-3.6524-2.587-6.0186 0-4.586 3.7293-8.3152 8.3152-8.3152 1.483 0 2.875.3912 4.082 1.0751l.8351-1.5262C15.481 2.395 13.8034 1.927 12.018 1.927 6.4746 1.9246 1.963 6.4362 1.963 11.982zm18.3702 0c0 4.586-3.7293 8.3152-8.3152 8.3152-1.4327 0-2.7837-.3648-3.962-1.0055l-.852 1.5166c1.4303.7823 3.0718 1.2287 4.814 1.2287 5.5434 0 10.055-4.5116 10.055-10.055 0-2.8077-1.1567-5.3467-3.0165-7.1729l-1.183 1.2743c1.519 1.507 2.4597 3.5924 2.4597 5.8986zm-1.9486 0c0 3.5109-2.8558 6.3642-6.3642 6.3642a6.3286 6.3286 0 01-3.0069-.756l-.8471 1.507c1.147.624 2.4597.9768 3.854.9768 4.4636 0 8.0944-3.6308 8.0944-8.0944 0-2.239-.9143-4.2692-2.3902-5.7378l-1.1783 1.267c1.1351 1.152 1.8383 2.731 1.8383 4.4732zm-14.4586 0c0 2.3014.9671 4.382 2.515 5.8578l1.1734-1.2695c-1.207-1.159-1.9606-2.786-1.9606-4.5883 0-3.5108 2.8557-6.3642 6.3642-6.3642 1.1423 0 2.215.3048 3.1437.8352l.8303-1.5167c-1.1759-.6647-2.5317-1.0487-3.974-1.0487-4.4612 0-8.092 3.6308-8.092 8.0944zm12.5292 0c0 2.4502-1.987 4.4372-4.4372 4.4372a4.4192 4.4192 0 01-2.0614-.5088l-.8351 1.4879a6.1135 6.1135 0 002.8965.727c3.3885 0 6.1434-2.7548 6.1434-6.1433 0-1.6774-.6767-3.1989-1.7686-4.3076l-1.1615 1.2503c.7559.7967 1.2239 1.8718 1.2239 3.0573zm-10.5806 0c0 1.7374.7247 3.3069 1.8886 4.4252L8.92 15.1569l.0144.0144c-.8351-.8063-1.3559-1.9366-1.3559-3.1869 0-2.4502 1.9846-4.4372 4.4372-4.4372.8087 0 1.5646.2184 2.2174.5976l.8207-1.4975a6.097 6.097 0 00-3.0381-.8063c-3.3837-.0048-6.141 2.7525-6.141 6.141zm6.681 0c0 .2952-.2424.5351-.5376.5351-.2952 0-.5375-.24-.5375-.5351 0-.2976.24-.5375.5375-.5375.2952 0 .5375.24.5375.5375zm-3.9405 0c0-1.879 1.5239-3.4029 3.4005-3.4029 1.879 0 3.4005 1.5215 3.4005 3.4029 0 1.879-1.5239 3.4005-3.4005 3.4005S8.6151 13.861 8.6151 11.982zm.1488 0c.0048 1.7974 1.4567 3.2493 3.2517 3.2517 1.795 0 3.254-1.4567 3.254-3.2517-.0023-1.7974-1.4566-3.2517-3.254-3.254-1.795 0-3.2517 1.4566-3.2517 3.254Z"]
  };

  var SERVICES = [
    { name: "Spotify", color: "#1DB954", icon: "spotify", url: function (q) { return "https://open.spotify.com/search/" + q; } },
    { name: "YouTube", color: "#FF0000", icon: "youtube", url: function (q) { return "https://www.youtube.com/results?search_query=" + q; } },
    { name: "Amazon", color: "#FF9900", icon: "amazon", url: function (q) { return "https://www.amazon.it/s?k=" + q + "&i=popular"; } },
    { name: "Discogs", color: "#333333", icon: "discogs", url: function (q) { return "https://www.discogs.com/search/?type=release&q=" + q; } },
    { name: "RYM", color: "#4270d8", icon: "rym", url: function (q) { return "https://rateyourmusic.com/search?searchterm=" + q + "&searchtype=l"; } }
  ];

  function makeIcon(s) {
    if (s.badge) {
      var b = document.createElement("span");
      b.className = "provider__badge";
      b.style.background = s.color;
      b.textContent = s.badge;
      return b;
    }
    var svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("class", "provider__icon");
    svg.setAttribute("fill", s.color);
    svg.setAttribute("aria-hidden", "true");
    ICON[s.icon].forEach(function (d) {
      var p = document.createElementNS(SVGNS, "path");
      p.setAttribute("d", d);
      svg.appendChild(p);
    });
    return svg;
  }

  function fillProviderLinks(container, a) {
    var q = encodeURIComponent(((a.artist ? a.artist + " " : "") + a.album).trim());
    var label = albumLabel(a);
    container.replaceChildren();
    SERVICES.forEach(function (s) {
      var link = document.createElement("a");
      link.className = "provider";
      link.href = s.url(q);
      link.target = "_blank";
      link.rel = "noopener";
      link.setAttribute("aria-label", "Cerca " + label + " su " + s.name);
      link.appendChild(makeIcon(s));
      var t = document.createElement("span");
      t.textContent = s.name;
      link.appendChild(t);
      container.appendChild(link);
    });
  }

  ALBUMS.forEach(function (a) {
    a._hay = fold(a.artist + " " + a.album + " " + (a.year || ""));
    a._decade = decadeOf(a.year);
    a._pop = typeof POPULARITY[a.id] === "number" ? POPULARITY[a.id] : -1;
  });

  var PAGE_SIZE = 25;
  var page = 1;

  var els = {
    search: $("search"),
    decade: $("decade"),
    sort: $("sort"),
    reset: $("reset"),
    grid: $("grid"),
    empty: $("empty"),
    count: $("count"),
    pager: $("pager"),
    prev: $("prev"),
    next: $("next"),
    pagerInfo: $("pagerInfo"),
    footerCount: $("footerCount"),
  };

  if (els.footerCount) els.footerCount.textContent = String(ALBUMS.length);

  /* ---- elemento copertina ---- */
  function initials(a) {
    var words = (a.album || "").split(/\s+/).filter(Boolean);
    return words.slice(0, 2).map(function (w) { return w[0]; }).join("").toUpperCase() || "?";
  }
  function coverFor(a, extraClass) {
    var node;
    var src = COVERS[a.id];
    if (src) {
      node = document.createElement("img");
      node.className = "cover";
      node.src = src;
      node.alt = "Copertina di " + a.album + (a.artist ? " - " + a.artist : "");
      node.loading = "lazy";
      node.decoding = "async";
      node.width = 500;
      node.height = 500;
    } else {
      node = document.createElement("div");
      node.className = "cover cover--placeholder";
      node.setAttribute("aria-hidden", "true");
      node.textContent = initials(a);
    }
    if (extraClass) node.classList.add(extraClass);
    return node;
  }

  /* ---- modal (vista estesa) ---- */
  var overlay = $("overlay");
  var modalEls = {
    cover: $("mCover"),
    artist: $("mArtist"),
    title: $("mTitle"),
    year: $("mYear"),
    links: $("mLinks"),
    close: $("mClose"),
    dialog: overlay ? overlay.querySelector(".modal") : null,
  };
  var lastFocus = null;

  function openModal(a) {
    modalEls.cover.replaceChildren(coverFor(a, "cover--modal"));
    modalEls.artist.textContent = a.artist || "Artista ignoto";
    modalEls.title.textContent = a.album;
    modalEls.year.textContent = a.year || "anno ignoto";
    fillProviderLinks(modalEls.links, a);
    lastFocus = document.activeElement;
    overlay.hidden = false;
    document.body.classList.add("modal-open");
    modalEls.close.focus();
  }
  function closeModal() {
    if (overlay.hidden) return;
    overlay.hidden = true;
    document.body.classList.remove("modal-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (overlay) {
    modalEls.close.addEventListener("click", closeModal);
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeModal();
      // focus trap semplice: tiene il focus dentro la modal
      if (e.key === "Tab" && !overlay.hidden) {
        var f = modalEls.dialog.querySelectorAll("a[href], button");
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  function makeClickable(node, a) {
    node.classList.add("is-clickable");
    node.tabIndex = 0;
    node.setAttribute("role", "button");
    node.setAttribute("aria-haspopup", "dialog");
    node.setAttribute("aria-label",
      "Apri " + a.album + (a.artist ? " di " + a.artist : "") + (a.year ? " (" + a.year + ")" : ""));
    node.addEventListener("click", function () { openModal(a); });
    node.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openModal(a); }
    });
  }

  /* ---- disco del giorno ---- */
  (function () {
    if (!ALBUMS.length) return;
    var now = new Date();
    var doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
    var a = ALBUMS[doy % ALBUMS.length];
    var daily = $("daily");
    daily.insertBefore(coverFor(a, "cover--daily"), daily.firstChild);
    $("dailyText").textContent =
      albumLabel(a) + (a.year ? " (" + a.year + ")" : "");
    makeClickable(daily, a);
  })();

  /* ---- opzioni decennio ---- */
  Array.from(new Set(ALBUMS.map(function (a) { return a._decade; }).filter(Boolean)))
    .sort(function (x, y) { return x - y; })
    .forEach(function (d) {
      var o = document.createElement("option");
      o.value = String(d);
      o.textContent = d + "s";
      els.decade.appendChild(o);
    });

  function highlightInto(node, text, q) {
    if (!q) { node.textContent = text; return; }
    var i = fold(text).indexOf(q);
    if (i === -1) { node.textContent = text; return; }
    node.appendChild(document.createTextNode(text.slice(0, i)));
    var m = document.createElement("mark");
    m.textContent = text.slice(i, i + q.length);
    node.appendChild(m);
    node.appendChild(document.createTextNode(text.slice(i + q.length)));
  }

  function cardFor(a, q) {
    var li = document.createElement("li");
    li.className = "card";
    li.appendChild(coverFor(a));

    var body = document.createElement("div");
    body.className = "card__body";

    var artist = document.createElement("span");
    artist.className = "card__artist";
    highlightInto(artist, a.artist || "Artista ignoto", q);

    var album = document.createElement("span");
    album.className = "card__album";
    highlightInto(album, a.album, q);

    var year = document.createElement("span");
    year.className = "card__year";
    year.textContent = a.year || "-";

    body.appendChild(artist);
    body.appendChild(album);
    body.appendChild(year);
    li.appendChild(body);
    makeClickable(li, a);
    return li;
  }

  var SORTERS = {
    artist: function (a, b) {
      return cmp(a.artist, b.artist) || (a.year || 0) - (b.year || 0) || cmp(a.album, b.album);
    },
    album: function (a, b) {
      return cmp(a.album, b.album) || cmp(a.artist, b.artist);
    },
    "year-asc": function (a, b) {
      return (a.year || Infinity) - (b.year || Infinity) || cmp(a.artist, b.artist) || cmp(a.album, b.album);
    },
    "year-desc": function (a, b) {
      return (b.year || -Infinity) - (a.year || -Infinity) || cmp(a.artist, b.artist) || cmp(a.album, b.album);
    },
    popularity: function (a, b) {
      return b._pop - a._pop || cmp(a.artist, b.artist) || cmp(a.album, b.album);
    },
  };
  function cmp(x, y) { return fold(x).localeCompare(fold(y)); }

  function render() {
    var q = fold(els.search.value.trim());
    var dec = els.decade.value ? Number(els.decade.value) : null;

    var results = ALBUMS.filter(function (a) {
      if (dec !== null && a._decade !== dec) return false;
      if (q && a._hay.indexOf(q) === -1) return false;
      return true;
    });
    results.sort(SORTERS[els.sort.value] || SORTERS.artist);

    var total = results.length;
    var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (page > pages) page = pages;
    if (page < 1) page = 1;
    var start = (page - 1) * PAGE_SIZE;
    var slice = results.slice(start, start + PAGE_SIZE);

    var frag = document.createDocumentFragment();
    slice.forEach(function (a) { frag.appendChild(cardFor(a, q)); });
    els.grid.replaceChildren(frag);

    var none = total === 0;
    els.empty.hidden = !none;
    els.count.textContent =
      total === ALBUMS.length ? ALBUMS.length + " dischi" : total + " / " + ALBUMS.length;

    els.pager.hidden = total <= PAGE_SIZE;
    els.prev.disabled = page <= 1;
    els.next.disabled = page >= pages;
    els.pagerInfo.textContent =
      none ? "" : (start + 1) + "-" + Math.min(start + PAGE_SIZE, total) + " | pagina " + page + "/" + pages;
  }

  function resetPageAndRender() { page = 1; render(); }

  els.search.addEventListener("input", resetPageAndRender);
  els.decade.addEventListener("change", resetPageAndRender);
  els.sort.addEventListener("change", resetPageAndRender);
  els.prev.addEventListener("click", function () {
    if (page > 1) { page--; render(); window.scrollTo({ top: 0 }); }
  });
  els.next.addEventListener("click", function () {
    page++; render(); window.scrollTo({ top: 0 });
  });
  $("random").addEventListener("click", function () {
    openModal(ALBUMS[Math.floor(Math.random() * ALBUMS.length)]);
  });
  els.reset.addEventListener("click", function () {
    els.search.value = "";
    els.decade.value = "";
    els.sort.value = "artist";
    page = 1;
    render();
    els.search.focus();
  });

  /* ---- pop-up "contribuisci" (riducibile a icona, stato in localStorage) ---- */
  (function () {
    var box = $("contribute");
    if (!box) return;
    var KEY = "ddg-contribute-min";
    var minimized = false;
    try { minimized = localStorage.getItem(KEY) === "1"; } catch (e) {}
    function setMin(on) {
      box.classList.toggle("contribute--min", on);
      try { localStorage.setItem(KEY, on ? "1" : "0"); } catch (e) {}
    }
    box.hidden = false; // sempre visibile: pieno o ridotto a icona
    if (minimized) box.classList.add("contribute--min");
    $("contribClose").addEventListener("click", function () { setMin(true); });
    $("contribOpen").addEventListener("click", function () { setMin(false); });
  })();

  render();
})();
