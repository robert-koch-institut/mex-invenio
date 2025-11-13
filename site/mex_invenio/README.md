# Managing translations in React components

## Required packages:
`i18next`, `react-i18next`, `i18next-browser-languagedetector`, `i18next-conv`

## Generation of translation json files

From `/site/mex_invenio` folder run:
```
i18next-conv -l {lang} -s ../../translations/{lang}/LC_MESSAGES/messages.po -t ./locales/{lang}/translation.json
```
for both `de` and `en` languages

### Using translations in custom components

To use the translations in a component import `useTranslations` from `react-i18next`, and use the `useTranslation` hook to get the `t` function and `i18n` instance.

```
import React from "react";
import { useTranslation } from 'react-i18next';

export const Record = ({ mexId, title }) => {
  const { t, i18n } = useTranslation();
  
  return (
      <h2>{t('Welcome to React')}</t2>
  );
};
```

