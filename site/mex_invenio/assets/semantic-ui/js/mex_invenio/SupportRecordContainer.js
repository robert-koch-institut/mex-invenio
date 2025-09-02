import {SupportRecordData} from "./SupportRecordData";

import React from "react";
import ReactDOM from "react-dom";

const supportRecordDiv = document.getElementById("support-record");

ReactDOM.render(
    <SupportRecordData />, // React component to render.
    supportRecordDiv // Target container on where to render the React components.
);