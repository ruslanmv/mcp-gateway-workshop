
(function () {
  'use strict';
  function mount() {
    // minimal decorative script
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();
