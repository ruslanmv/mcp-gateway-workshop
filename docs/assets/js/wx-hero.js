(function () {
  'use strict';
  function mount() {
    // Minimal decorative script (no-op to avoid JS errors)
    // You can add particle effects later if you like.
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();
