const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8020/api/files";

export async function getFiles(path?: string) {
  const url = path ? `${API_BASE}?path=${encodeURIComponent(path)}` : API_BASE;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`GET /api/files failed: ${res.status}`);
  return res.json();
}

// Upload with progress callback: progress in [0..1]
export function uploadFileWithProgress(file: File, opts: { path?: string; comment?: string } = {}, onProgress?: (p: number) => void) {
  return new Promise<any>((resolve, reject) => {
    const form = new FormData();
    form.append("attachment", file); // ВАЖНО: backend принимает 'attachment'
    form.append("fields", JSON.stringify({ path: opts.path || "", comment: opts.comment || "" }));

    const xhr = new XMLHttpRequest();
    xhr.open("POST", API_BASE, true);

    xhr.upload.onprogress = (ev) => {
      if (ev.lengthComputable && onProgress) onProgress(ev.loaded / ev.total);
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try { resolve(JSON.parse(xhr.responseText)); } catch (e) { resolve(xhr.responseText); }
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    };

    xhr.onerror = () => reject(new Error("Upload network error"));
    xhr.send(form);
  });
}

export async function deleteFile(id: number) {
  const res = await fetch(`${API_BASE}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
  return res.json();
}

export async function downloadFile(id: number) {
  const res = await fetch(`${API_BASE}/${id}/download`);
  if (!res.ok) throw new Error("Download failed");
  const blob = await res.blob();
  // Попытка получить имя из content-disposition
  const cd = res.headers.get("content-disposition");
  let filename = `file-${id}`;
  if (cd) {
    const m = /filename\*?=(?:UTF-8'')?["']?([^;"']+)/i.exec(cd);
    if (m) filename = decodeURIComponent(m[1]);
  }
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function updateFile(id: number, fields: Record<string, any>) {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fields }),
  });
  if (!res.ok) throw new Error("Update failed");
  return res.json();
}

export async function syncFiles() {
  const res = await fetch(`${API_BASE}/sync`, { method: "POST" });
  if (!res.ok) throw new Error("Sync failed");
  return res.json();
}
