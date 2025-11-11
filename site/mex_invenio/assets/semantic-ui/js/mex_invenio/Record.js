import React from "react";
import { useData } from "./useData";
import { settings } from "./includes/settings"
import { DisplayValues } from "./includes/DisplayValue";


export const Record = ({ mexId, title }) => {
  const { data, loading, error } = useData(mexId);

  if (loading) return <p>Loading… { mexId }</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error.message}</p>;

  const invenio_id = data["id"]

  return <div className="recordContent">
    <p className="record--ids">{ mexId } | <a href={`/api/records/${ invenio_id }`}> { invenio_id } </a></p>
      <table class="ui table">
      <caption><h2 className="ui header">{ title }</h2></caption>
      {Object.entries(data.normalised).map(([key, value]) => (
          key !== "backwards_linked" &&
          <tr className="row props">
            <th class="props-label">{ key }</th>
            <td><DisplayValues key={key} values={value} /></td>
          </tr>
      ))}
      </table>
    </div>
;
}