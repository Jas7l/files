"use client"

import { useState } from "react"
import type { FileItem } from "../types"
import EditFileModal from "./EditFileModal"
// Импортируем функции из правильных файлов
import { deleteFile, downloadFile } from "../api/files"
import { apiFetch } from "../api/http" // apiFetch из http.ts

interface FileActionsProps {
  file: FileItem
  onFileDeleted: () => void
  onFileUpdated: () => void
}

export default function FileActions({ file, onFileDeleted, onFileUpdated }: FileActionsProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  const handleDownload = async () => {
    try {
      // Используем функцию из api/files.ts
      await downloadFile(file.id)
    } catch (error) {
      console.error("Ошибка при скачивании:", error)
      alert("Не удалось скачать файл")
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Вы уверены, что хотите удалить файл "${file.name}"?`)) {
      return
    }

    setIsDeleting(true)
    try {
      // Используем функцию из api/files.ts
      await deleteFile(file.id)
      onFileDeleted()
    } catch (error) {
      console.error("Ошибка при удалении:", error)
      alert("Не удалось удалить файл")
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <>
      <div className="file-actions">
        <button onClick={handleDownload} className="action-btn action-btn-download">
          <svg className="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          <span className="action-label">Скачать</span>
        </button>

        <button onClick={() => setIsEditModalOpen(true)} className="action-btn action-btn-edit">
          <svg className="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
          <span className="action-label">Изменить</span>
        </button>

        <button onClick={handleDelete} disabled={isDeleting} className="action-btn action-btn-delete">
          <svg className="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
          <span className="action-label">{isDeleting ? "Удаление..." : "Удалить"}</span>
        </button>
      </div>

      {isEditModalOpen && (
        <EditFileModal file={file} onClose={() => setIsEditModalOpen(false)} onFileUpdated={onFileUpdated} />
      )}
    </>
  )
}