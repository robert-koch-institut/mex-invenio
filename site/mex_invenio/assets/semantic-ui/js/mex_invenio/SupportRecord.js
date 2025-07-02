import HelloWorld from "./HelloWorld";

import React from "react";
import ReactDOM from "react-dom";

const supportRecordContainer = document.getElementById("support-record");

ReactDOM.render(
    <HelloWorld />, // React component to render.
    supportRecordContainer // Target container on where to render the React components.
);