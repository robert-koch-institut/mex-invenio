import React, { useState } from 'react';
import { Record } from './Record';
import CloseIcon from "./includes/Close";

export const SupportRecordData = ({mexId, closeModalFn}) => {
  
  return (
    <div id={`${mexId}-record`} className="ui right very wide modal custom-modal">
      <div className="custom-modal-header">
        <CloseIcon closeModalFn={closeModalFn}/>
      </div>
      <div className="scrolling content">
        <h2 className="ui header">Record</h2>
        <Record mexId={mexId} />
      </div>
    </div>
  );
};