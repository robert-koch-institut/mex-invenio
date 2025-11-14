# Managing translations in React components

1. Go to `/site/mex_invenio` folder
2. Install dependencies `npm install`
3. run `npm run convert-po` to translate `translations/de/LC_MESSAGES/messages.po` and `translations/en/LC_MESSAGES/messages.po` to `json`
4. run `npm run extract-messages` to extract strings from js files located in `site/mex_invenio/assets/semantic-ui/js/mex_invenio`

## Using translations in custom components

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

