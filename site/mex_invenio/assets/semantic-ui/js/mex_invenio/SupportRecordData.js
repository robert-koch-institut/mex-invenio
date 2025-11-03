import React, { useState } from 'react';
import { Record } from './Record';
import CloseIcon from "./includes/Close";

export const SupportRecordData = ({mexId, title, closeModalFn}) => {
  
  return (
    <div id={`${mexId}-record`} className="ui right very wide modal custom-modal">
      <div className="custom-modal-header">
        <CloseIcon closeModalFn={closeModalFn}/>
      </div>
      <div className="scrolling content" style={{ maxHeight: '90vh' }}>
        <Record mexId={mexId} title={title} />
      </div>
    </div>
  );
}; 