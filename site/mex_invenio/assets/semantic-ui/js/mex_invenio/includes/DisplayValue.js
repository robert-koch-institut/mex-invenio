import React, { useState } from 'react';
import { Button } from 'semantic-ui-react';
import { settings } from './settings';
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

const DisplayValues = ({
  values,
}) => {
  const maxVisible = 3;
  const total = values.length;
  const visible = values.slice(0, maxVisible);
  const hidden = values.slice(maxVisible);
  const [showAll, setShowAll] = useState(false);
  if (!Array.isArray(values)) {
    values = [values]
  }

  return (
    <div className="card-prop-value">
      {visible.map((v, index) => (
        <DisplayValue
          key={index}
          v={v}
        />
      ))}

      {hidden.length > 0 && (
        <>
          <div className="more-values" style={{ display: showAll ? 'block' : 'none' }}>
            {hidden.map((v, index) => (
              <DisplayValue
                key={maxVisible + index}
                v={v}
              />
            ))}
          </div>

          <Button
            type="button"
            className="link-like"
            onClick={() => setShowAll(!showAll)}
          >
            {showAll ? `t("Show less") ▲` : `t("Show all") (${total}) ▼`}
          </Button>
        </>
      )}
    </div>
  );
};

const DisplayValue = ({ v }) => {
  const supportRecordHandler = (mex_id, combined_title) => {
    window.dispatchEvent(
      new CustomEvent("supportRecord:update", {
        detail: { mex_id, combined_title }
      })
    );
  };

  const combineTitles = (items) => items.map(d => d.value).join(', ');

  const lang = "en";
  const dd = v.display_data || [];
  const correctLang = dd.filter(d => d.language === lang);
  const emptyLang = dd.filter(d => d.language === '');

  const selected =
    correctLang.length > 0
      ? [...correctLang, ...emptyLang]
      : dd;

  const combinedTitle = combineTitles(selected);

  // ─────────────────────────
  // Simple external link
  // ─────────────────────────
  if (v.url && v.url.includes("http")) {
    return (
      <a
        href={v.url}
        title={combinedTitle}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Open link: ${combinedTitle}`}
      >
        {combinedTitle}
      </a>
    );
  }

  // ─────────────────────────
  // Internal link with “core” icon
  // ─────────────────────────
  if (v.url && v.core) {
    return (
      <a
        href={v.url}
        title={combinedTitle}
        aria-label={`Open ${combinedTitle}`}
      >
        <div className="tags">
          <span className="tag">
            <img
              className="ui image icon--text"
              src={`/static/icons/${v.core}-record.svg`}
              alt=""
              role="presentation"
            />
            <span className="sr-only">{settings.CORE_ENTITIES[v.core]}</span>
          </span>
          {combinedTitle}
        </div>
      </a>
    );
  }

  // ─────────────────────────
  // Internal navigation via CustomEvent
  // ─────────────────────────
  if (v.url) {
    return (
      <Button
        className="link-like"
        data-record-id={v.url}
        onClick={() => supportRecordHandler(v.url, combinedTitle)}
        aria-label={`Open modal with record ${combinedTitle}`}
      >
        {combinedTitle}
      </Button>
    );
  }

  // ─────────────────────────
  // Plain text content
  // ─────────────────────────
  return <p>{combinedTitle}</p>;
};

export { DisplayValues, DisplayValue };
