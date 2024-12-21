import { use } from 'i18next';
import xhr from 'i18next-xhr-backend';
import { initReactI18next } from 'react-i18next';

const i18n =
  // load translation using xhr -> see /public/locales
  // learn more: https://github.com/i18next/i18next-xhr-backend
  use(xhr)
    // pass the i18n instance to react-i18next
    .use(initReactI18next)
    // init i18next
    // for all options read: https://www.i18next.com/overview/configuration-options
    .init({
      debug: process.env.NODE_ENV === 'development',
      lng: 'ru',
      fallbackLng: 'ru',
      defaultNS: 'translation',
      interpolation: {
        escapeValue: false // not needed for react as it escapes by default
      },
      react: {
        useSuspense: false
      },
      backend: {
        loadPath: '/static/v2/js/locales/{{lng}}/{{ns}}.json'
      }
    });

export default i18n;
