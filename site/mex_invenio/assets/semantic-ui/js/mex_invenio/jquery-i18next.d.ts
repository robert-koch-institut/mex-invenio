declare module 'jquery-i18next' {
  const jqueryI18next: {
    init: (i18next: any, $: any, options?: any) => void;
  };
  export default jqueryI18next;
}

declare global {
  interface JQuery {
    localize(): JQuery;
    i18n(): JQuery;
  }
}
