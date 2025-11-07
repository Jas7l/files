import React, { useEffect, useState } from "react";
import { getFiles, syncFiles } from "../api/files";
import FileUpload from "../components/FileUpload";
import FileList from "../components/FileList";
import type { FileItem } from "../types";

export default function Home() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await getFiles();
      setFiles(data || []);
    } catch (e) { console.error(e); alert(String(e)); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Облачное хранилище</h1>
        <div className="flex gap-2">
          <button onClick={async () => { await syncFiles(); load(); }} className="bg-blue-600 text-white px-3 py-1 rounded">Синхронизировать</button>
          <button onClick={load} className="bg-gray-200 px-3 py-1 rounded">Обновить</button>
        </div>
      </div>

      <FileUpload onDone={load} />

      {loading ? <p className="mt-4">Загрузка...</p> : <FileList files={files} onRefresh={load} />}
    </div>
  );
}
