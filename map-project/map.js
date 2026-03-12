/* ═══════════════════════════════════════════════════════════════════════════
   Rachakonda Layout — Interactive Plot Map Script
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const STATUS_LABELS = {
    available:  'Available',
    sold:       'Sold Out',
    booked:     'Booked',
    registered: 'Registered',
  };

  const PILL_CLASS = {
    available:  'pill-available',
    sold:       'pill-sold',
    booked:     'pill-booked',
    registered: 'pill-registered',
  };

  let selectedPlot = null;
  let currentData  = null;

  // ── 1. Load SVG into viewport ──────────────────────────────────────────

  async function loadMap() {
    const viewport = document.getElementById('map-viewport');
    try {
      const resp = await fetch('map.svg');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const svgText = await resp.text();
      viewport.innerHTML = svgText;
      init();
    } catch (err) {
      viewport.innerHTML = '<p style="padding:2em;text-align:center;color:#c44">Failed to load map.svg</p>';
      console.error('Map load error:', err);
    }
  }

  // ── 2. Initialize after SVG is injected ────────────────────────────────

  function init() {
    computeStats();
    bindPlotClicks();
    bindModalClose();
  }

  // ── 3. Stats computation ───────────────────────────────────────────────

  function computeStats() {
    const plots = document.querySelectorAll('.plot');
    const counts = { available: 0, sold: 0, booked: 0, registered: 0 };
    plots.forEach(p => {
      const st = p.getAttribute('data-status');
      if (st in counts) counts[st]++;
    });

    document.getElementById('cA').textContent = counts.available;
    document.getElementById('cS').textContent = counts.sold;
    document.getElementById('cB').textContent = counts.booked;
    document.getElementById('cR').textContent = counts.registered;
    document.getElementById('cT').textContent = plots.length;
  }

  // ── 4. Click handler for plots ─────────────────────────────────────────

  function bindPlotClicks() {
    document.querySelectorAll('.plot').forEach(el => {
      el.addEventListener('click', () => selectPlot(el));
    });
  }

  function selectPlot(el) {
    if (selectedPlot) selectedPlot.classList.remove('selected');
    selectedPlot = el;
    el.classList.add('selected');

    const label  = el.getAttribute('data-label');
    const status = el.getAttribute('data-status') || 'available';
    const sqyd   = el.getAttribute('data-sqyd')   || '400';

    currentData = { label, status, sqyd };
    console.log('Selected plot:', label, status);

    // Populate modal
    document.getElementById('mN').textContent = 'Plot ' + label;

    const pill = document.getElementById('mP');
    pill.textContent = STATUS_LABELS[status] || status;
    pill.className = 'mpill ' + (PILL_CLASS[status] || 'pill-available');

    document.getElementById('mI').textContent = label;
    document.getElementById('mS').textContent = STATUS_LABELS[status] || status;
    document.getElementById('mArea').textContent = sqyd + ' sq.yd';

    const cta = document.getElementById('mC');
    if (status === 'available') {
      cta.textContent = '\uD83D\uDCDE Enquire About This Plot';
      cta.className = 'cta';
    } else {
      cta.textContent = '\u2713 ' + (STATUS_LABELS[status] || status);
      cta.className = 'cta disabled';
    }

    document.getElementById('backdrop').classList.add('on');
  }

  // ── 5. Modal close ─────────────────────────────────────────────────────

  function bindModalClose() {
    const backdrop = document.getElementById('backdrop');

    // Close button
    document.getElementById('modal-close').addEventListener('click', closeModal);

    // Backdrop click
    backdrop.addEventListener('click', e => {
      if (e.target === backdrop) closeModal();
    });

    // Escape key
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeModal();
    });

    // Enquiry CTA
    document.getElementById('mC').addEventListener('click', enquire);
  }

  function closeModal() {
    document.getElementById('backdrop').classList.remove('on');
    if (selectedPlot) {
      selectedPlot.classList.remove('selected');
      selectedPlot = null;
    }
  }

  // ── 6. Enquiry action ──────────────────────────────────────────────────

  function enquire() {
    if (currentData && currentData.status === 'available') {
      alert(
        'Please contact us about Plot ' + currentData.label + '.\n\n' +
        'Lohitha Dharma Projects Pvt. Ltd.'
      );
    }
  }

  // ── Boot ───────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', loadMap);
})();
