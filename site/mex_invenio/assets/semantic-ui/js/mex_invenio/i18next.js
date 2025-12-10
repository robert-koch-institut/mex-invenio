/* global $, i18n */

// Expose i18next globally for vanilla JavaScript
window.i18next = i18n;

// Optional helper functions for easier DOM translations
window.translateById = (id, key, options = {}) => {
  const el = document.getElementById(id);
  if (el) el.textContent = window.i18next.t(key, options);
};

window.translateBySelector = (selector, key, options = {}) => {
  document.querySelectorAll(selector).forEach((el) => {
    el.textContent = window.i18next.t(key, options);
  });
};
