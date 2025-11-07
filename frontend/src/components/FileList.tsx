import React, { useState } from "react";
import type { FileItem } from "../types";
import { deleteFile, downloadFile, updateFile } from "../api/files";

export default function FileList({ files, onRefresh }: { files: FileItem[]; onRefresh: () => void }) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editComment, setEditComment] = useState("");

  function startEdit(f: FileItem) {
    setEditingId(f.id);
    setEditName(f.name);
    setEditComment(f.comment || "");
  }

  async function saveEdit(id: number) {
    try {
      await updateFile(id, { name: editName, comment: editComment });
      setEditingId(null);
      onRefresh();
    } catch (e) { alert(String(e)); }
  }

  return (
    <table className="w-full mt-4">
      <thead>
        <tr className="text-left border-b">
          <th className="p-2">Имя</th>
          <th className="p-2">Расширение</th>
          <th className="p-2">Размер</th>
          <th className="p-2">Комментарий</th>
          <th className="p-2">Действия</th>
        </tr>
      </thead>
      <tbody>
        {files.map(f => (
          <tr key={f.id} className="border-b hover:bg-gray-50">
            <td className="p-2">
              {editingId === f.id ? (
                <input value={editName} onChange={e => setEditName(e.target.value)} />
              ) : (
                <span>{f.name}</span>
              )}
            </td>
            <td className="p-2">{f.extension}</td>
            <td className="p-2">{(f.size / 1024).toFixed(1)} KB</td>
            <td className="p-2">
              {editingId === f.id ? (
                <input value={editComment} onChange={e => setEditComment(e.target.value)} />
              ) : (
                <span>{f.comment}</span>
              )}
            </td>
            <td className="p-2 space-x-2">
              <button onClick={() => downloadFile(f.id)} className="text-blue-600">Скачать</button>
              <button onClick={() => startEdit(f)} className="text-yellow-600">Изменить</button>
              <button onClick={async () => { if(confirm('Удалить файл?')) { await deleteFile(f.id); onRefresh(); }}} className="text-red-600">Удалить</button>
              {editingId === f.id && (
                <>
                  <button onClick={() => saveEdit(f.id)} className="text-green-600">Сохранить</button>
                  <button onClick={() => setEditingId(null)} className="text-gray-600">Отмена</button>
                </>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
