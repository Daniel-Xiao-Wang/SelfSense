import * as React from "react";
import * as ReactDOM from "react-dom/client";
import App from "./App";
import Info from "./Info";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";

const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement);

root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="info" element={<Info />} />
    </Routes>
  </BrowserRouter>
);
