// Entry point of the React app. Start reading here.
//
// This file mounts React into index.html and defines the routes, i.e. which
// page shows for which URL:
//   /, /host       -> Host  (the host's TV or laptop)
//   /join/:code    -> Join  (guests land here from the QR code)
//   /room/:roomId  -> Room  (guests search, add songs, and vote)
// To add a new page, create it in src/pages/ and add a <Route> below.

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Host from "./pages/Host.jsx";
import Join from "./pages/Join.jsx";
import Room from "./pages/Room.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Host />} />
        <Route path="/host" element={<Host />} />
        <Route path="/join/:code" element={<Join />} />
        <Route path="/room/:roomId" element={<Room />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
