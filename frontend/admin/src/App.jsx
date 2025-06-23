// frontend/admin/src/App.jsx

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import SettingsPage from "./pages/SettingsPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/settings" replace />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/upload" element={<UploadPage />} />
      </Routes>
    </BrowserRouter>
  );
}
