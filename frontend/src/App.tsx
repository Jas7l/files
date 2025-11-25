"use client"

import { useState, useEffect } from "react"
import FileTree from "./components/FileTree"
import UploadFile from "./components/UploadFile"
import type { FileItem } from "./types"

function App() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchFiles = async () => {
    try {
      setLoading(true)
      const res = await fetch("http://localhost:8020/api/files")
      if (!res.ok) {
        throw new Error(`Ошибка ${res.status}`)
      }
      const data = await res.json()
      setFiles(data)
      setError(null)
    } catch (err) {
      console.error("Ошибка при загрузке файлов:", err)
      setError("Не удалось загрузить список файлов")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFiles()
  }, [])

  const handleFileDeleted = () => {
    fetchFiles()
  }

  const handleFileUpdated = () => {
    fetchFiles()
  }

  const handleFileUploaded = () => {
    fetchFiles()
  }

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p className="loading-text">Загрузка...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-error">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
      </div>
    )
  }

  return (
    <div className="app-container">
      <header className="app-header-bar">
        <div className="header-bar-content">
          <svg className="header-bar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          </svg>
          <h1 className="header-bar-title">Облачное хранилище</h1>
          <span className="header-bar-count">
            {files.length} {files.length === 1 ? "файл" : files.length < 5 ? "файла" : "файлов"}
          </span>
        </div>
      </header>

      <div className="app-content">
        <div className="content-grid">
          <div className="files-section">
            <FileTree files={files} onFileDeleted={handleFileDeleted} onFileUpdated={handleFileUpdated} />
          </div>

          <div className="upload-sidebar">
            <UploadFile onFileUploaded={handleFileUploaded} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
