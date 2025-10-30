import React from "react";
import { useData } from "./useData";


export const Record = ({ mexId }) => {
  const { data, loading, error } = useData(mexId);

  if (loading) return <p>Loading… { mexId }</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error.message}</p>;

  const invenio_id = data["id"]
  const title = data["custom_fields"]["mex:alternativeName"]

  return <div className="recordContent">
    <p className="record--ids">{ mexId } | <a href={`/api/records/${ invenio_id }`}> { invenio_id } </a></p>
    <div className="data">
      {JSON.stringify(data, null, 2)}
    </div>
  </div>
;
}