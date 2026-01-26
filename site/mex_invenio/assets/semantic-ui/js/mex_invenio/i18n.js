/* global $ */
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import deTranslations from "./locales/de/translations.json";
import enTranslations from "./locales/en/translations.json"

console.log("INIT FILE LOADED");

const resources = {
  de: { mextranslations: deTranslations },
  en: { mextranslations: enTranslations },
};

console.log('Custom resources de.mextranslations.Welcome:', resources.de.mextranslations?.Welcome);
console.log('Custom resources en.mextranslations.Welcome:', resources.en.mextranslations?.Welcome);

// Global ready flag
window.i18nReady = false;

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    lng: window.APP_CONFIG?.current_lang || 'de',
    resources,
    fallbackLng: "en",
    supportedLngs: ["de", "en"],
    ns: ['mextranslations'],
    defaultNS: 'mextranslations',
    debug: true,
    returnNull: false,
    interpolation: { escapeValue: false },
    react: { useSuspense: false }
  }, (err, t) => {
    if (err) return console.error(err);
    window.i18nReady = true;
    console.log('i18n CALLBACK ready, t(Welcome):', t('Welcome'));
  });

export default i18n;
