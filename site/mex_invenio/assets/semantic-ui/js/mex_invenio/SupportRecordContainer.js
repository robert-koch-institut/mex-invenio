import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { SupportRecordData } from "./SupportRecordData";

const SupportRecordRoot = () => {
  const initialId =
    document.getElementById("support-record")?.dataset.recordId || null;

  const [recordId, setRecordId] = useState(initialId);
  const [recordTitle, setRecordTitle] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = (event) => {
      const { mex_id, combined_title } = event.detail;
      setRecordId(mex_id);
      setRecordTitle(combined_title);
      setOpen(true); // keep modal open or reopen it
    };

    window.addEventListener("supportRecord:update", handler);
    return () => window.removeEventListener("supportRecord:update", handler);
  }, []);

  const closeModal = () => setOpen(false);

  return (
    open && (
      <SupportRecordData
        mexId={recordId}
        title={recordTitle}
        closeModalFn={closeModal}
      />
    )
  );
};

const supportRecordDiv = document.getElementById("support-record");
if (supportRecordDiv) {
  ReactDOM.render(<SupportRecordRoot />, supportRecordDiv);
}
