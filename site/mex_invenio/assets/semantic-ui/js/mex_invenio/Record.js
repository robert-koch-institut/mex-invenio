import React, { useState } from "react";
import { useData } from "./useData";
import { DisplayValues } from "./includes/DisplayValue";
import { Table, Header } from 'semantic-ui-react';
import { useTranslation } from 'react-i18next';


export const Record = ({ mexId, title }) => {
  const { t } = useTranslation();
  const { data, loading, error } = useData(mexId);
  const [copyStatus, setCopyStatus] = useState("idle");


  if (loading) return <p role="status">Loading… {mexId}</p>;
  if (error) return <p role="alert" style={{ color: "red" }}>Error: {error.message}</p>;

  const invenio_id = data.id;


  const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    setCopyStatus("success");

    // reset message after 2 seconds
    setTimeout(() => setCopyStatus("idle"), 2000);
  } catch (err) {
    console.error("Copy failed:", err);
    setCopyStatus("error");

    setTimeout(() => setCopyStatus("idle"), 2000);
  }
};



  const smartT = (key) => {
    const key_without_context = key.replace("mex:", "") + ".singular";
    const key_with_context = key.replace("mex:", "") + ".singular_" + data["metadata"]["resource_type"]["id"];
    return t(key_without_context) == key_without_context ? t(key_with_context) : t(key_without_context);
  }

  return (
    <div className="recordContent card card--only-layout">
      <p className="record--ids">
        <span className="muted">{mexId} </span>
        <span className="click-to-copy">
          <button
            type="button"
            onClick={() => copyToClipboard(mexId)}
            aria-label={t("Copy mexId")}
            title={t("Copy mexId")}
          >
            <img
              className="ui image icon"
              src="/static/icons/copy.svg"
              alt=""
              aria-hidden="true"
            />
          </button>
        </span>
        <span className="muted"> | </span>
        <a  href={`/api/records/${invenio_id}`} aria-label={`View record ${invenio_id} as JSON`} >{invenio_id}</a>
      </p>

      {copyStatus === "success" && (
        <span
          className="copied-msg"
          role="status"
          aria-live="polite"
        >
          {t("Copied!")}
        </span>
      )}

      {copyStatus === "error" && (
        <span
          className="copied-msg error"
          role="alert"
        >
          {t("Copy failed")}
        </span>
      )}

      <Header as="h3">{t(title)}</Header>
      <div className="card-props">
        {Object.entries(data.normalised)
          .filter(([key]) => key !== "backwards_linked" && key !== "mex:identifier")
          .map(([key, value]) => (
            <div key={key} className="row card-props-p" verticalAlign="top">
              <div className="key card-prop-label">
                {smartT(key)}
              </div>
              <DisplayValues values={value} />
            </div>
          ))}
      </div>
    </div>
  );
};
