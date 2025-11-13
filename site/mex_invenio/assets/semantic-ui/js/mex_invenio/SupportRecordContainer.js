import React, { useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom";
import './i18n';
import { SupportRecordData } from "./SupportRecordData";

const SupportRecordRoot = () => {
  const initialId =
    document.getElementById("support-record")?.dataset.recordId || null;

  const [recordId, setRecordId] = useState(initialId);
  const [recordTitle, setRecordTitle] = useState("");
  const [open, setOpen] = useState(false);

  const historyStack = useRef([]);

  useEffect(() => {
    const handler = (event) => {
      const { mex_id, combined_title } = event.detail;

      if (open && recordId) {
        historyStack.current.push({
          recordId,
          recordTitle,
        });
      }

      setRecordId(mex_id);
      setRecordTitle(combined_title);
      setOpen(true);
    };

    window.addEventListener("supportRecord:update", handler);
    return () => window.removeEventListener("supportRecord:update", handler);
  }, [open, recordId, recordTitle]);

  const closeModal = () => {
    setOpen(false);
    historyStack.current = [];
  };

  const goBack = () => {
    const prev = historyStack.current.pop();
    if (!prev) {
      setOpen(false);
      return;
    }
    setRecordId(prev.recordId);
    setRecordTitle(prev.recordTitle);
    setOpen(true);
  };

  // Title of the modal you would return to
  const previousTitle =
    historyStack.current.length > 0
      ? historyStack.current[historyStack.current.length - 1].recordTitle
      : null;

  return (
    open && (
      <SupportRecordData
        mexId={recordId}
        title={recordTitle}
        closeModalFn={closeModal}
        goBackFn={goBack}
        previousTitle={previousTitle}    // <-- pass it down
      />
    )
  );
};

const supportRecordDiv = document.getElementById("support-record");
if (supportRecordDiv) {
  ReactDOM.render(<SupportRecordRoot />, supportRecordDiv);
}
