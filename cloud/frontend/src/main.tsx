import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { DeviceGate } from "./components/DeviceGate";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <DeviceGate>
      <App />
    </DeviceGate>
  </React.StrictMode>,
);
