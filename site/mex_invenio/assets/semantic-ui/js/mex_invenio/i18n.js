import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import deTranslations from "./locales/de/translation.json";

const resources = {
    de: { translation: deTranslations },
};

const initializeI18n =() => {
    i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        lng: window.APP_CONFIG["current_lang"],
        resources,
        fallbackLng: "en",
        supportedLngs: ["de", "en"],
        load: "currentOnly",
        detection: {
            order: ['cookie', 'localStorage', 'sessionStorage', 'navigator', 'htmlTag'],
            caches: ['cookie','localStorage'],
        },
        debug: true,
        interpolation: {
            escapeValue: false,
        },
});
};

const intervalId = setInterval(() => {
    console.log("check! ")
        if (window.APP_CONFIG && window.APP_CONFIG["current_lang"]) {
            clearInterval(intervalId);
            initializeI18n()
        }
}, 100);