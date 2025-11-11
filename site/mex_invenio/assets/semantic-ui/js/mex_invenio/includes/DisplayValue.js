import React, { useState } from 'react';

const DisplayValue = ({ v }) => {

    const supportRecordHandler = (mex_id, combined_title) => {
        window.dispatchEvent(
            new CustomEvent("supportRecord:update", { detail: { mex_id, combined_title } })
        );
    }; 

    const combineTitles = (items) => items.map(d => d.value).join(', ');

    const lang = "en";
    const dd = v.display_data;
    let selected = [];

    const correctLang = dd.filter(d => d.language === lang);
    if (correctLang.length > 0) {
        const emptyLang = dd.filter(d => d.language === '');
        selected = [...correctLang, ...emptyLang];
    } else {
        selected = dd;
    }

    const combinedTitle = combineTitles(selected);
  
    if (v.url) {
        if (v.url.includes("http")){ 
            return (
                <a href={ v.url } title={ combinedTitle }>
                    { combinedTitle }
                </a>
            )
        }
        else if (v.core) {
            return (
                <a href={v.url} title={combinedTitle}>
                    <div className="tags">
                        <span className="tag">
                            <img
                                className="ui image icon--text"
                                src={`/static/icons/${v.core}-record.svg`}
                                role="presentation"
                                alt=""
                            />
                            (--Record type--)   
                        </span>
                        {combinedTitle}
                    </div>
                </a>
            );
        } else {
            return (
                <button
                    type="button"
                    className="ui button link-like"
                    data-record-id={v.url}
                    onClick={() => supportRecordHandler(v.url, combinedTitle)}
                >
                {combinedTitle}
                </button>
            );
        }
    } else {
        return <p>{combinedTitle}</p>;
    }
};

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
    <>
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

          <button
            type="button"
            className="ui button link-like"
            onClick={() => setShowAll(!showAll)}
          >
            {showAll ? 'Show less ▲' : `Show all (${total}) ▼`}
          </button>
        </>
      )}
    </>
  );
};

export { DisplayValues, DisplayValue };