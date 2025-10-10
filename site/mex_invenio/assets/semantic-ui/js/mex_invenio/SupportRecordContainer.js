import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { SupportRecordData } from "./SupportRecordData";

const SupportRecordRoot = () => {
  const [recordId, setRecordId] = useState(
    document.getElementById("support-record")?.dataset.recordId || null
  );

  // Listen for custom events from plain JS
  useEffect(() => {
    const handler = (event) => { 
        console.log("handler");
        console.log(event.detail);
        setRecordId(event.detail.mex_id);
    }
    window.addEventListener("supportRecord:update", handler);
    return () => window.removeEventListener("supportRecord:update", handler);
  }, []);

  return recordId ? <SupportRecordData mex_id={recordId} /> : <p>Nothing here yet</p>;
};

const supportRecordDiv = document.getElementById("support-record");
if (supportRecordDiv) {
  ReactDOM.render(<SupportRecordRoot />, supportRecordDiv);
}
