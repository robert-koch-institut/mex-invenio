import React, { useState } from 'react';
const DisplayValue = ({ v }) => {
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
    if (v.core) {
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
                onClick={() => console.log("support record clicked")}
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


// {% macro display_values(values, max) %}
//     {% set max_visible = max if max else config.get("VALUES_DISPLAYED_DEFAULT", 3) %}

//     {% set total = values | length %}
//     {% set visible = values[:max_visible] %}
//     {% set hidden = values[max_visible:] %}

//     {%- for v in visible  -%}
//         {{ display_value(v) }}
//     {%- endfor -%}

//     {# If there are more, show "Add more" button #}
//     {% if hidden %}
//         <div class="more-values" style="display: none;">
//             {% for v in hidden %}
//                 {{ display_value(v) }}
//             {% endfor %}
//         </div>
//         <button
//             type="button"
//             class="ui button link-like"
//             onclick="
//                 const hidden = this.previousElementSibling;
//                 const isHidden = hidden.style.display === 'none';
//                 hidden.style.display = isHidden ? 'block' : 'none';
//                 this.textContent = isHidden ? 'Show less &#x25B4;' : 'Show all ({{ total }}) &#x25BE;';
//             "
//         >
//             Show all ({{ total }}) &#x25BE;
//         </button>
//     {% endif %}

// {% endmacro %}

// {% macro display_value(v) %}
//     {%- if v.url -%}
//         {%- if v.core -%}
//             {%- set lang = current_i18n.language -%}
//             {%- set dd = v["display_data"] -%}
//             {%- if dd[0].language -%}
//                 {%- set correct_lang = dd | selectattr("language", "equalto", lang) | list -%}
//                 {%- if correct_lang | length > 0 -%}
//                     {%- set empty_lang = dd | selectattr("language", "equalto", "") | list -%}
//                     {%- set selected = correct_lang  + empty_lang -%}
//                 {%- else -%}
//                     {%- set selected = dd -%}
//                 {%- endif -%}
//             {%- else -%}
//                 {%- set selected = dd -%}
//             {%- endif -%}
//             {% set ns = namespace(titles=[]) %}
//             {% for s in selected %}
//                 {% set _ = ns.titles.append(s.value) %}
//             {% endfor %}
//             {% set combined_title = ns.titles | join(', ') %}
//             <a href="{{ v.url }}" title="{{ combined_title }}">
//                 <div class="tags"><span class="tag"><img class="ui image icon--text"
//                  src="{{ url_for('static', filename='icons/' ~ v.core ~ '-record.svg') }}"
//                  role="presentation"/> {{ config.UI_SETTINGS[v.core].label }}</span>
//                 {{ combined_title }}
//                 </a></div>
//         {%- else -%}
//             {% set ns = namespace(titles=[]) %}
//             {% for dv in v["display_data"] %}
//                 {% set _ = ns.titles.append(dv.value) %}
//             {% endfor %}
//             {% set combined_title = ns.titles | join(', ') %}
//             <button type="button" class="ui button link-like" data-record-id="{{ v.url }}?normlised" onclick="supportRecordHandler('{{ v.url }}')">{{ combined_title }}</button>
//         {%- endif -%}
//     {%- else -%}
//         {% set ns = namespace(titles=[]) %}
//         {% for dv in v["display_data"] %}
//             {% set _ = ns.titles.append(dv.value) %}
//         {% endfor %}
//         {% set combined_title = ns.titles | join(', ') %}
//         <p>{{combined_title }}</p>
//     {%- endif -%}
// {% endmacro %}
