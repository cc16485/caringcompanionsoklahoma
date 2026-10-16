// Caring Companions Oklahoma: interactive service area map (Leaflet + CARTO light tiles).
// Data: assets/service-area.geojson (4 counties + 17 ZIPs, with drive minutes from the Mustang office).
(function () {
  'use strict';
  var el = document.getElementById('sa-map');
  if (!el) return;
  if (!window.L) { el.classList.add('sa-map-failed'); return; }

  var OFFICE = [35.3842, -97.7245]; // Mustang
  var DEEP = '#14606F', TEAL = '#1F7A8C', MINT = '#8FD1C7', NAVY = '#0D365F', HONEY = '#F0A63A';
  var mobile = window.matchMedia('(max-width: 720px)').matches;

  var map = L.map(el, {
    scrollWheelZoom: false,
    dragging: true,
    tap: false,
    zoomSnap: 0.25,
    attributionControl: true
  });
  if (mobile) map.dragging.disable();

  var ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/';
  L.tileLayer(ESRI + 'World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
    attribution: 'Basemap &copy; <a href="https://www.esri.com/">Esri</a>, HERE, Garmin, &copy; OpenStreetMap contributors'
  }).addTo(map);
  map.createPane('labels');
  map.getPane('labels').style.zIndex = 650;
  map.getPane('labels').style.pointerEvents = 'none';
  L.tileLayer(ESRI + 'World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16, pane: 'labels'
  }).addTo(map);

  function shade(min) {
    if (min == null) return TEAL;
    if (min <= 15) return '#0F5563';
    if (min <= 25) return '#3E98A8';
    return '#A9DDD5';
  }
  function zipStyle(f) {
    return { color: '#ffffff', weight: 1.5, fillColor: shade(f.properties.minutes), fillOpacity: 0.62 };
  }
  var countyStyle = { color: NAVY, weight: 2, dashArray: '6 6', fill: true, fillColor: NAVY, fillOpacity: 0.03, interactive: false };

  var zipLayers = {}, countyLayers = {}, selected = null, zipGroup, countyGroup;

  function popupHtml(p) {
    var t = p.minutes != null ? '<p class="sa-pop-time">About ' + p.minutes + ' minutes from our Mustang office</p>' : '';
    return '<div class="sa-pop"><p class="sa-pop-zip">' + p.zip + '</p><p class="sa-pop-area">' + p.area + '</p>' +
      (p.county ? '<p class="sa-pop-county">' + p.county + '</p>' : '') + t +
      '<a class="sa-pop-btn" href="contact.html">Book a free visit</a></div>';
  }

  function select(layer) {
    if (selected && selected !== layer) zipGroup.resetStyle(selected);
    selected = layer;
    layer.setStyle({ fillColor: HONEY, fillOpacity: 0.7, weight: 2.5, color: '#ffffff' });
    layer.bringToFront();
  }

  fetch('assets/service-area.geojson').then(function (r) { return r.json(); }).then(function (data) {
    var counties = data.features.filter(function (f) { return f.properties.kind === 'county'; });
    var zips = data.features.filter(function (f) { return f.properties.kind === 'zip'; });

    countyGroup = L.geoJSON(counties, {
      style: countyStyle,
      onEachFeature: function (f, layer) { countyLayers[f.properties.name] = layer; }
    }).addTo(map);

    // Which counties each ZIP touches (from the site's ZIP list, embedded in the page).
    var zipCounties = window.SA_ZIP_COUNTIES || {};

    zipGroup = L.geoJSON(zips, {
      style: zipStyle,
      onEachFeature: function (f, layer) {
        var p = f.properties;
        p.county = zipCounties[p.zip] ? zipCounties[p.zip] + (zipCounties[p.zip].indexOf(',') > -1 ? ' counties' : ' County') : '';
        zipLayers[p.zip] = layer;
        layer.bindTooltip('<b>' + p.zip + '</b> ' + p.area, { sticky: true, direction: 'top', className: 'sa-tip' });
        layer.bindPopup(popupHtml(p), { className: 'sa-popup', closeButton: true, autoPanPadding: [24, 24] });
        layer.on({
          mouseover: function () { if (layer !== selected) layer.setStyle({ fillOpacity: 0.72, weight: 2.5 }); },
          mouseout: function () { if (layer !== selected) zipGroup.resetStyle(layer); },
          click: function () { select(layer); }
        });
      }
    }).addTo(map);

    // County name labels at the visual centre of each county
    counties.forEach(function (f) {
      var short = f.properties.name.replace(' County', ''), served = null;
      zipGroup.eachLayer(function (l) {
        var cs = zipCounties[l.feature.properties.zip] || '';
        if (cs.split(', ')[0] === short) served = served ? served.extend(l.getBounds()) : L.latLngBounds(l.getBounds().getSouthWest(), l.getBounds().getNorthEast());
      });
      var c = (served || countyLayers[f.properties.name].getBounds()).getCenter();
      L.marker(c, {
        interactive: false, keyboard: false,
        icon: L.divIcon({ className: 'sa-county-label', html: '<span>' + f.properties.name + '</span>', iconSize: null })
      }).addTo(map);
    });

    // Office marker
    var officeIcon = L.divIcon({
      className: 'sa-office',
      iconSize: [46, 46], iconAnchor: [23, 23],
      html: '<span class="sa-office-pulse"></span><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="22" fill="#fff" stroke="' + NAVY + '" stroke-width="3"/><path d="M13 23 24 14l11 9v11a2 2 0 0 1-2 2H15a2 2 0 0 1-2-2z" fill="#EAF4F6" stroke="' + NAVY + '" stroke-width="2.4" stroke-linejoin="round"/><path d="M24 33s-5.5-3.2-5.5-6.7a2.8 2.8 0 0 1 5.5-.9 2.8 2.8 0 0 1 5.5.9c0 3.5-5.5 6.7-5.5 6.7z" fill="' + TEAL + '"/><circle cx="24" cy="20" r="2.4" fill="' + HONEY + '"/></svg>'
    });
    L.marker(OFFICE, { icon: officeIcon, zIndexOffset: 1000, title: 'Our Mustang office' })
      .bindPopup('<div class="sa-pop"><p class="sa-pop-zip">Our office</p><p class="sa-pop-area">Mustang, Oklahoma</p><p class="sa-pop-time">Open Monday to Friday, 8am to 6pm</p></div>', { className: 'sa-popup' })
      .addTo(map);

    var all = zipGroup.getBounds();
    function fitAll() { map.fitBounds(all, { padding: mobile ? [8, 8] : [16, 16] }); }
    fitAll();
    window.addEventListener('resize', function () { map.invalidateSize(); });

    // County buttons
    document.querySelectorAll('[data-county]').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('[data-county]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true');
        var name = b.getAttribute('data-county');
        if (name === 'all') { fitAll(); return; }
        var cl = countyLayers[name];
        if (!cl) return;
        // Zoom to where we actually serve inside this county
        var inside = null;
        zipGroup.eachLayer(function (l) {
          var cs = zipCounties[l.feature.properties.zip] || '';
          if (cs.indexOf(name.replace(' County', '')) > -1) inside = inside ? inside.extend(l.getBounds()) : L.latLngBounds(l.getBounds().getSouthWest(), l.getBounds().getNorthEast());
        });
        map.fitBounds(inside || cl.getBounds(), { padding: [30, 30] });
      });
    });

    // ZIP checker
    var form = document.getElementById('sa-check');
    if (form) {
      var input = form.querySelector('input'), out = document.getElementById('sa-result');
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var z = (input.value || '').replace(/\D/g, '').slice(0, 5);
        out.className = 'sa-result';
        if (z.length !== 5) { out.textContent = 'Please enter a 5-digit ZIP code.'; return; }
        var layer = zipLayers[z];
        if (layer) {
          var p = layer.feature.properties;
          out.classList.add('yes');
          out.innerHTML = '<b>Yes, we serve ' + z + '.</b> ' + p.area + (p.minutes != null ? ', about ' + p.minutes + ' minutes from our office.' : '.') + ' <a href="contact.html">Book a free visit</a>';
          map.fitBounds(layer.getBounds(), { padding: [60, 60], maxZoom: 13 });
          select(layer);
          layer.openPopup(layer.getBounds().getCenter());
        } else {
          out.classList.add('no');
          out.innerHTML = '<b>' + z + ' isn\'t in our area yet.</b> Give us a call anyway and we\'ll talk it through.';
          fitAll();
        }
      });
    }
  }).catch(function () { el.classList.add('sa-map-failed'); });
})();
