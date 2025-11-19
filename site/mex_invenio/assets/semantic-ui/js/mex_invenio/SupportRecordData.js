import React, {useEffect} from 'react';
import { Modal, Button } from 'semantic-ui-react';
import { Record } from './Record';
import CloseIcon from "./includes/Close";

export const SupportRecordData = ({
    mexId,
    title,
    closeModalFn,
    goBackFn,
    previousTitle
}) => {

    useEffect(() => {
        const modal = document.getElementById(`${mexId}-record`);
        modal?.focus();
    }, []);

    return (
        <Modal
            id={`${mexId}-record`}
            open={true}
            className="right very wide custom-modal"
            size="large"
            role="dialog"
            aria-modal="true"
            aria-labelledby={`${mexId}-record-title`}
            closeOnDimmerClick={true}
            closeOnEscape={true}
            onClose={closeModalFn}
        >
            <div className="custom-modal-header">
                <CloseIcon closeModalFn={closeModalFn} />

                {previousTitle && (
                <Button
                    type="button"
                    className="link-like back ui button"
                    onClick={goBackFn}
                    aria-label={`Back to ${previousTitle}`}
                >
                    <span aria-hidden="true">←</span> Back to: {previousTitle}
                </Button>
                )}
            </div>

            <Modal.Content className="content">
                <div className="scrolling" 
                    style={{ maxHeight: '85vh', overflowY: "scroll" }}
                    role="region"
                    tabIndex={-1}
                    aria-label="Record content"
                >
                <Record mexId={mexId} title={title} />
                </div>
            </Modal.Content>
        </Modal>
  );
};
