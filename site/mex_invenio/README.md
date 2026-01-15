# General development

Before each commit, make sure to run the linter and tests:

The linter runs pre-commit run --all-files

```bash
make lint
```

For running unit tests you need to have the test dependencies installed.

```bash
pipenv install --dev
```

Make sure not to have any Invenio services or an instance running because the tests run a Docker instance
through `docker-services-cli`.

```bash
make test
```

# Translation Compilation Process

The translation system combines Python (.po) files with JavaScript translations through a multi-step process.
The structure of the translations folder (./translations) is as follows:

```
.
├── babel.ini - Configuration file for Babel
├── de
│   └── LC_MESSAGES
│        ├── messages.mo - Compiled translation file
│        ├── messages.po - Merged translation file (mex-model + UI)
│        ├── messages.po.backup - Backup of previous messages.po
│        └── ui.po - UI-specific translation file
├── en
│   └── LC_MESSAGES
│        ├── messages.mo
│        ├── messages.po
│        ├── messages.po.backup
│        └── ui.po
```

For backend translations to work correctly, the compiled `messages.mo` files must exist. For frontend translations,
the `messages.po` files are converted to JSON format like so:

- **mex-model translations**: Base translations from the `mex.model` package (German/English .po files)
  These are located in the folder [mex/model/i18n](https://github.com/robert-koch-institut/mex-model/tree/main/mex/model/i18n)
- **UI-specific translations**: Located in `translations/{lang}/LC_MESSAGES/ui.po` for custom UI strings
- **Merged output**: Combined into `translations/{lang}/LC_MESSAGES/messages.po`

## Deployment Steps

### Step 1: Merge translations
```bash
python ./site/mex_invenio/scripts/merge_translations.py ${INVENIO_INSTANCE_PATH}
```
- Merges mex-model base translations with UI-specific translations
- UI translations take precedence over base translations, the lookup is done by a combination of
  `msgctxt` (if available) and `msgid`, for example: `publisher.singular` has different translations depending
  on context,
- Creates backup files before overwriting as `translations/{lang}/LC_MESSAGES/messages.po.backup`
- The process is hardcoded for only the two languages German and English.

### Step 2: Install npm dependencies
```bash
cd site/mex_invenio
npm install
```

### Step 3: Convert .po to JSON
```bash
npm run convert-po
```
- Converts `translations/de/LC_MESSAGES/messages.po` → `assets/semantic-ui/js/mex_invenio/locales/de/translations.json`
- Converts `translations/en/LC_MESSAGES/messages.po` → `assets/semantic-ui/js/mex_invenio/locales/en/translations.json`

### Step 4: Compile Python translations
```bash
invenio-cli translations compile
```
Compiles the `messages.po` files into binary `messages.mo` files for backend use.


## Development Instructions
1. Go to `/site/mex_invenio` folder
2. Install dependencies `npm install`
3. Run `npm run convert-po` to convert .po files to JSON
4. Run `npm run extract-messages` to extract strings from JS files located in `site/mex_invenio/assets/semantic-ui/js/mex_invenio`

## Using translations in custom components

To use the translations in a component import `useTranslations` from `react-i18next`, and use the `useTranslation`
hook to get the `t` function and `i18n` instance.

```jsx
import React from "react";
import { useTranslation } from 'react-i18next';

export const Record = ({ mexId, title }) => {
  const { t, i18n } = useTranslation();

  return (
      <h2>{t('Welcome to React')}</h2>
  );
};
```

## Using translations in Jinja2 templates

Macros are available from `templates/semantic-ui/invenio_app_rdm/records/macros/mex_detail.html`, a macro called
`smart_translate` can be used to translate strings in Jinja2 templates. It takes two arguments: `context` and `msgid`.
The context is always the resource type (.e.g. 'resource', 'activity', 'person').

```html
{% from "semantic-ui/invenio_app_rdm/records/macros/mex_detail.html" import smart_translate %}

<h1>{{ smart_translate('resource', 'publisher.singular') }}</h1>
```

Smart_translate needs to be used for all translations coming from the mex-model,
as these translations are context-dependent.