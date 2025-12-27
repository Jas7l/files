import { apiFetch } from "./http";

export interface StorageStats {
  total_used_mb: number;
  limit_mb: number;
  free_mb: number;
  by_category_mb: {
    audio: number;
    video: number;
    images: number;
    documents: number;
    other: number;
  };
}

export async function getStorageStats(): Promise<StorageStats> {
  const res = await apiFetch("/api/files/stats");
  if (!res.ok) throw new Error(`Failed to get storage stats: ${res.status}`);
  return res.json();
}