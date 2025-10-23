import React from "react";
import { useData } from "./useData";
import CloseIcon from "./includes/Close";

export const Record = ({ mex_id }) => {
  const { data, loading, error } = useData({mex_id});

  if (loading) return <p>Loading…</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error.message}</p>;

  return <div class="ui right very wide modal custom-modal">
          <div className="custom-modal-header">
            <CloseIcon />
          </div>
            <div className="scrolling content">
              <h2 className="ui header">Record</h2>
              <div className="ui list user-info">
                <div className="item">
                  {JSON.stringify(data, null, 2)}
                </div>
              </div>
            </div>
        </div>
;
}