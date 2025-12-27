"use client"

import { useState, useEffect } from "react"
import FileTree from "../components/FileTree"
import StorageStats from "../components/StorageStats"
import Header from "../components/Header"
import DragDropZone from "../components/DragDropZone"
import type { FileItem } from "../types"
import { getFiles } from "../api/files"

export default function StoragePage() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  const [uploadTrigger, setUploadTrigger] = useState(0)

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

  const handleFileDeleted = () => {
    fetchFiles(search)
    // Триггерим обновление статистики
    setUploadTrigger(prev => prev + 1)
  }

  const handleFileUpdated = () => {
    fetchFiles(search)
    // Триггерим обновление статистики
    setUploadTrigger(prev => prev + 1)
  }

  const handleFileUploaded = () => {
    fetchFiles(search)
    // Триггерим обновление статистики
    setUploadTrigger(prev => prev + 1)
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearch(value)
    fetchFiles(value)
  }

  return (
    <div style={styles.container}>
      <Header />
      <div style={styles.content}>
        {/* Основная область с файлами */}
        <div style={styles.mainContent}>
          <input
            type="text"
            placeholder="Поиск файлов..."
            value={search}
            onChange={handleSearchChange}
            style={styles.searchInput}
          />

          {/* Обернем область списка файлов в DragDropZone */}
          <div style={styles.fileTreeContainer}>
            <DragDropZone onFileUploaded={handleFileUploaded}>
              {loading && <p style={styles.loadingText}>Загрузка...</p>}
              {error && <p style={styles.errorText}>{error}</p>}
              {!loading && !error && (
                <FileTree
                  files={files}
                  onFileDeleted={handleFileDeleted}
                  onFileUpdated={handleFileUpdated}
                />
              )}
            </DragDropZone>
          </div>
        </div>

        {/* Панель статистики - без скролла, просто часть страницы */}
        <div style={styles.statsPanel}>
          <StorageStats key={uploadTrigger} onFileUploaded={handleFileUploaded} />
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: "100%",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#f4f7f6",
  },
  content: {
    flex: 1,
    display: "flex",
    gap: 20,
    padding: 20,
    boxSizing: "border-box",
  },
  mainContent: {
    flex: 3,
    display: "flex",
    flexDirection: "column",
    gap: 12,
    minWidth: 0,
  },
  searchInput: {
    padding: "10px 14px",
    fontSize: 14,
    borderRadius: 8,
    border: "1px solid #d1d5db",
    backgroundColor: "white",
    boxShadow: "0 1px 2px rgba(0, 0, 0, 0.05)",
    width: "100%",
    boxSizing: "border-box",
  },
  fileTreeContainer: {
    flex: 1,
    backgroundColor: "white",
    borderRadius: 8,
    border: "1px solid #e5e7eb",
    overflow: "hidden",
    minHeight: 400,
  },
  statsPanel: {
    flex: 1,
    minWidth: 320,
    maxWidth: 400,
    alignSelf: "flex-start", // Чтобы не растягивалась
  },
  loadingText: {
    fontSize: 16,
    color: "#333",
    padding: 20,
    textAlign: "center",
  },
  errorText: {
    fontSize: 16,
    color: "red",
    padding: 20,
    textAlign: "center",
  },
}