import React, { useState } from "react";
import { uploadFileWithProgress } from "../api/files";

export default function FileUpload({ onDone }: { onDone: () => void }) {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  async function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadFileWithProgress(file, {}, (p) => setProgress(p));
      onDone();
    } catch (err) {
      alert(String(err));
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }

  return (
    <div className="p-4 border-2 border-dashed rounded-md">
      <input type="file" onChange={onFileChange} disabled={uploading} />
      {uploading && (
        <div className="mt-2">
          <div className="w-full bg-gray-200 rounded h-2">
            <div style={{ width: `${Math.round(progress * 100)}%` }} className="h-2 bg-blue-600 rounded" />
          </div>
          <div className="text-sm mt-1">{Math.round(progress * 100)}%</div>
        </div>
      )}
    </div>
  );
}
