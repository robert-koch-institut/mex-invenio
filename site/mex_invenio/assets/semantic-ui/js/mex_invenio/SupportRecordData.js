import React, { useState } from 'react';
import { Record } from './Record';
import CloseIcon from "./includes/Close";

export const SupportRecordData = ({mexId, title, closeModalFn, goBackFn, previousTitle}) => {
  
  return (
    <div id={`${mexId}-record`} className="ui right very wide modal custom-modal">
        <div className="custom-modal-header">
            <CloseIcon closeModalFn={closeModalFn}/>
        </div>
        <div className="content">
            {previousTitle && (
                <button type="button" className="ui button link-like" onClick={goBackFn}>
                    ← Back to: {previousTitle}
                </button>
            )}
            <div className="scrolling" style={{ maxHeight: '90vh' }}>
                <Record mexId={mexId} title={title} />
            </div>
        </div>
    </div>
  );
}; 