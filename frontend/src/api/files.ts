import { apiFetch } from "./http";

const FILES_BASE = "/api/files";

export async function getFiles(path?: string) {
  const url = path ? `${FILES_BASE}?path=${encodeURIComponent(path)}` : FILES_BASE;
  const res = await apiFetch(url);
  if (!res.ok) throw new Error(`GET files failed: ${res.status}`);
  return res.json();
}

export async function uploadFileWithProgress(
  file: File,
  opts: { path?: string; comment?: string } = {},
  onProgress?: (p: number) => void
) {
  const form = new FormData();
  form.append("attachment", file);
  form.append("fields", JSON.stringify({ path: opts.path || "", comment: opts.comment || "" }));

  return new Promise<any>(async (resolve, reject) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        reject(new Error("No token found"));
        return;
      }

      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8020";
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_URL}${FILES_BASE}`, true);

      // Устанавливаем заголовок Authorization
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);

      // Также можно добавить другие заголовки если нужно
      // xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable && onProgress) {
          onProgress(ev.loaded / ev.total);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch (e) {
            resolve(xhr.responseText);
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status}`));
        }
      };

      xhr.onerror = () => reject(new Error("Upload network error"));
      xhr.send(form);
    } catch (err) {
      reject(err);
    }
  });
}

export async function deleteFile(id: number) {
  const res = await apiFetch(`${FILES_BASE}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
  return res.json();
}

export async function downloadFile(id: number) {
  const res = await apiFetch(`${FILES_BASE}/${id}/download`);
  if (!res.ok) throw new Error(`Download failed: ${res.status}`);

  const blob = await res.blob();
  const cd = res.headers.get("content-disposition");
  let filename = `file-${id}`;

  if (cd) {
    const m = /filename\*?=(?:UTF-8'')?["']?([^;"']+)/i.exec(cd);
    if (m) filename = decodeURIComponent(m[1]);
  }

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function updateFile(id: number, fields: Record<string, any>) {
  const res = await apiFetch(`${FILES_BASE}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fields }),
  });
  if (!res.ok) throw new Error(`Update failed: ${res.status}`);
  return res.json();
}

export async function syncFiles() {
  const res = await apiFetch(`${FILES_BASE}/sync`, { method: "POST" });
  if (!res.ok) throw new Error(`Sync failed: ${res.status}`);
  return res.json();
}