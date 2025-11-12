import React from "react";
import { useData } from "./useData";
import { DisplayValues } from "./includes/DisplayValue";
import { Table, Header } from 'semantic-ui-react'

export const Record = ({ mexId, title }) => {
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

      <Header as="h3">{title}</Header>
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
                <Table.Cell as="th" scope="row" className="key">{key.slice("mex:".length)}</Table.Cell>
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
