// jquery-i18next-esm.js
// Thin ES module wrapper around jquery-i18next

import $ from 'jquery';
import i18next from 'i18next';
import './jquery-i18next';

export function init(options = {}) {
  // jquery-i18next exposes a global-like init via $.i18n or similar,
  // depending on the version; this calls the integration setup.
  $.i18n.init(i18next, $, options);
}
