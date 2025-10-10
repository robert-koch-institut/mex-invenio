import React from 'react';
import { Record } from './Record';

export const SupportRecordData = ({mex_id}) => {

  return (
    <>
      <p><strong>url: </strong> {`/records/mex/${mex_id}/json`}</p>
      <Record mex_id={mex_id} />
    </>
  );
};