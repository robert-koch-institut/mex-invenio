import React from "react";
import { useData } from "./useData";
import { DisplayValues } from "./includes/DisplayValue";
import { Table, Header } from 'semantic-ui-react';
import { useTranslation } from 'react-i18next';


export const Record = ({ mexId, title }) => {
  const { t } = useTranslation();
  const { data, loading, error } = useData(mexId);

  if (loading) return <p role="status">Loading… {mexId}</p>;
  if (error) return <p role="alert" style={{ color: "red" }}>Error: {error.message}</p>;

  const invenio_id = data.id;

  const smartT = (key) => {
    const key_without_context = key.replace("mex:", "") + ".singular";
    const key_with_context = key.replace("mex:", "") + ".singular_" + data["metadata"]["resource_type"]["id"];
    return t(key_without_context) == key_without_context ? t(key_with_context) : t(key_without_context);
  }

  return (
    <div className="recordContent">
      <p className="record--ids">
        <span className="muted">{mexId} | </span>
        <a  href={`/api/records/${invenio_id}`} aria-label={`View record ${invenio_id} as JSON`} >{invenio_id}</a>
      </p>

      <Header as="h3">{t(title)}</Header>
      <Table celled className="record-modal">
        <Table.Header className="sr-only">
          <Table.Row verticalAlign='top'>
            <Table.HeaderCell>Field</Table.HeaderCell>
            <Table.HeaderCell>Value</Table.HeaderCell>
          </Table.Row>
        </Table.Header>

        {Object.entries(data.normalised)
          .filter(([key]) => key !== "backwards_linked" && key !== "mex:identifier")
          .map(([key, value]) => (
            <Table.Row key={key} className="row props" verticalAlign="top">
              <Table.Cell as="th" scope="row" className="key">
                {smartT(key)}
              </Table.Cell>
              <Table.Cell>
                <DisplayValues values={value} />
              </Table.Cell>
            </Table.Row>
          ))}
      </Table>
    </div>
  );
};
