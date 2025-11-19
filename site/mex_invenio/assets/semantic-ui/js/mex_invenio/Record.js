import React from "react";
import { useData } from "./useData";
import { DisplayValues } from "./includes/DisplayValue";
import { Table, Header } from 'semantic-ui-react';
import { useTranslation } from 'react-i18next';
// import { i18next } from "@translations/invenio_rdm_records/i18next"


export const Record = ({ mexId, title }) => {
  const { t, i18n } = useTranslation();
  const { data, loading, error } = useData(mexId);

  if (loading) return <p role="status">Loading… {mexId}</p>;
  if (error) return <p role="alert" style={{ color: "red" }}>Error: {error.message}</p>;

  const invenio_id = data.id;

  return (
    <div className="recordContent">
      <p className="record--ids">
        <span className="muted">{mexId} | </span>
        <a  href={`/api/records/${invenio_id}`} aria-label={`View record ${invenio_id} as JSON`} >{invenio_id}</a>
      </p>

      {/* <Header as="h2">{i18next.t('Welcome to React')}</Header> */}
      <Header as="h3">{t(title)}</Header>
      <Table celled>
        <Table.Header className="sr-only">
          <Table.Row verticalAlign='top'>
            <Table.HeaderCell>Field</Table.HeaderCell>
            <Table.HeaderCell>Value</Table.HeaderCell>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {Object.entries(data.normalised).map(([key, value]) =>
            key !== "backwards_linked" &&
            key !== "mex:identifier" ? (
              <Table.Row key={key} className="row props" verticalAlign='top'>
                <Table.Cell as="th" scope="row" className="key">{t(key)}</Table.Cell>
                <Table.Cell>
                  <DisplayValues values={value} />
                </Table.Cell>
              </Table.Row>
            ) : null
          )}
        </Table.Body>
      </Table>
    </div>
  );
};
