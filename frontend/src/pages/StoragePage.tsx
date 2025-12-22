"use client"

import { useState, useEffect } from "react"
import FileTree from "../components/FileTree"
import UploadFile from "../components/UploadFile"
import Header from "../components/Header"
import type { FileItem } from "../types"
import { getFiles } from "../api/files"

export default function StoragePage() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState("")

  const fetchFiles = async (filterPath = "") => {
    try {
      setLoading(true)
      const data = await getFiles(filterPath)
      setFiles(data)
      setError(null)
    } catch (err) {
      console.error(err)
      setError("Не удалось загрузить список файлов")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFiles()
  }, [])

  const handleFileDeleted = () => fetchFiles(search)
  const handleFileUpdated = () => fetchFiles(search)
  const handleFileUploaded = () => fetchFiles(search)

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearch(value)
    fetchFiles(value)
  }

  return (
    <div style={styles.container}>
      <Header />
      <div style={styles.content}>
        <div style={styles.fileTree}>
          <input
            type="text"
            placeholder="Поиск файлов..."
            value={search}
            onChange={handleSearchChange}
            style={styles.searchInput}
          />

          {loading && <p style={styles.loadingText}>Загрузка...</p>}
          {error && <p style={styles.errorText}>{error}</p>}
          {!loading && !error && (
            <FileTree files={files} onFileDeleted={handleFileDeleted} onFileUpdated={handleFileUpdated} />
          )}
        </div>

        <div style={styles.uploadSidebar}>
          <UploadFile onFileUploaded={handleFileUploaded} />
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: "100%",
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    backgroundColor: "#f4f7f6",
  },
  content: {
    flex: 1,
    display: "flex",
    gap: 16,
    padding: 16,
    boxSizing: "border-box",
    minWidth: 0,
    overflow: "hidden",
  },
  fileTree: {
    flex: 3,
    minWidth: 0,
    display: "flex",
    flexDirection: "column",
    gap: 8,
    overflowY: "auto",
    maxHeight: "100%",
  },
  uploadSidebar: {
    flex: 1,
    minWidth: 0,
    overflowY: "auto",
    maxHeight: "100%",
  },
  searchInput: {
    padding: "8px 12px",
    fontSize: 14,
    borderRadius: 6,
    border: "1px solid #ccc",
    marginBottom: 8,
    width: "100%",
    boxSizing: "border-box",
  },
  loadingText: {
    fontSize: 16,
    color: "#333",
  },
  errorText: {
    fontSize: 16,
    color: "red",
  },
}
