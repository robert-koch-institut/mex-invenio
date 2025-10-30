import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { SupportRecordData } from "./SupportRecordData";

const SupportRecordRoot = () => {
  const [recordId, setRecordId] = useState(
    document.getElementById("support-record")?.dataset.recordId || null
  );
  const [open, setOpen] = useState(false);

  // Listen for custom events from plain JS
  useEffect(() => {
    const handler = (event) => { 
        setRecordId(event.detail.mex_id);
        setOpen(true);
    }
    window.addEventListener("supportRecord:update", handler);
    return () => window.removeEventListener("supportRecord:update", handler);
  }, []);

  return open && (
  <SupportRecordData mexId={recordId} closeModalFn={() => setOpen(false)} />
);
};

const supportRecordDiv = document.getElementById("support-record");
if (supportRecordDiv) {
  ReactDOM.render(<SupportRecordRoot />, supportRecordDiv);
}
