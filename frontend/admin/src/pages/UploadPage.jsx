// frontend/admin/src/pages/UploadPage.jsx

import { useState } from "react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = e => setFile(e.target.files[0]);

  const handleUpload = () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    axios.post("http://localhost:8000/upload", form)
      .then(res => setMessage(`Uploaded: ${res.data.file_id}`))
      .catch(err => setMessage("Upload failed"));
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl mb-4">File Upload</h1>
      <input type="file" onChange={handleFileChange} />
      <button
        onClick={handleUpload}
        className="mt-4 px-4 py-2 bg-green-600 text-white rounded"
      >
        Upload
      </button>
      {message && <p className="mt-2">{message}</p>}
    </div>
  );
}
