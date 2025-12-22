"use client"

import type React from "react"
import { useState } from "react"
import type { FileItem } from "../types"
import { updateFile } from "../api/files"

interface EditFileModalProps {
  file: FileItem
  onClose: () => void
  onFileUpdated: () => void
}

export default function EditFileModal({ file, onClose, onFileUpdated }: EditFileModalProps) {
  // В состоянии храним относительный путь (relative_path из БД)
  const [name, setName] = useState(file.name || "")
  const [relativePath, setRelativePath] = useState(file.relative_path || "")
  const [comment, setComment] = useState(file.comment || "")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      // Подготавливаем объект fields для отправки
      const fields: Record<string, any> = {}

      // Добавляем только те поля, которые изменились
      if (name !== file.name) fields.name = name
      if (relativePath !== file.relative_path) fields.path = relativePath // Важно: отправляем как "path"
      if (comment !== file.comment) fields.comment = comment

      // Если ничего не изменилось - просто закрываем окно
      if (Object.keys(fields).length === 0) {
        onClose()
        return
      }

      console.log("Отправляемые поля:", fields) // Для отладки

      // Используем updateFile из files.ts
      const updatedFile = await updateFile(file.id, fields)
      console.log("Обновленный файл:", updatedFile) // Для отладки

      onFileUpdated() // Обновляем список файлов
      onClose() // Закрываем модальное окно

    } catch (error) {
      console.error("Ошибка при обновлении:", error)
      setError(error instanceof Error ? error.message : "Неизвестная ошибка")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" style={styles.overlay}>
      <div className="modal-content" style={styles.modal}>
        <div className="modal-header" style={styles.header}>
          <h2 className="modal-title" style={styles.title}>
            Редактировать файл: {file.name}
          </h2>
          <button
            onClick={onClose}
            className="modal-close"
            style={styles.closeButton}
            disabled={isSubmitting}
          >
            <svg className="modal-close-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body" style={styles.body}>
            {error && (
              <div className="error-message" style={styles.error}>
                <strong>Ошибка:</strong> {error}
              </div>
            )}

            <div className="form-group" style={styles.formGroup}>
              <label className="form-label" style={styles.label}>
                Имя файла (без расширения)
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="form-input"
                style={styles.input}
                placeholder="Введите новое имя файла"
                disabled={isSubmitting}
              />
              <div className="form-hint" style={styles.hint}>
                Текущее расширение: <strong>{file.extension}</strong>
              </div>
            </div>

            <div className="form-group" style={styles.formGroup}>
              <label className="form-label" style={styles.label}>
                Путь к файлу (относительный)
              </label>
              <input
                type="text"
                value={relativePath}
                onChange={(e) => setRelativePath(e.target.value)}
                className="form-input"
                style={styles.input}
                placeholder="Например: documents/projects или просто оставьте пустым для корня"
                disabled={isSubmitting}
              />
              <div className="form-hint" style={styles.hint}>
                Относительный путь внутри вашего хранилища. Текущее расположение: <strong>{file.relative_path || "(корень)"}</strong>
              </div>
              <div className="form-hint" style={styles.hint}>
                Примеры: "documents", "projects/2025", "images/photos"
              </div>
            </div>

            <div className="form-group" style={styles.formGroup}>
              <label className="form-label" style={styles.label}>
                Комментарий
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="form-textarea"
                style={styles.textarea}
                rows={3}
                placeholder="Добавьте описание или комментарий к файлу..."
                disabled={isSubmitting}
              />
            </div>

            <div className="file-info" style={styles.info}>
              <h3 style={styles.infoTitle}>Текущая информация:</h3>
              <ul style={styles.infoList}>
                <li><strong>ID:</strong> {file.id}</li>
                <li><strong>Полное имя:</strong> {file.name}.{file.extension}</li>
                <li><strong>Размер:</strong> {formatFileSize(file.size)}</li>
                <li><strong>Текущий путь:</strong> {file.path}{file.relative_path ? '/' + file.relative_path : ''}</li>
                <li><strong>UUID имя:</strong> {file.stored_name}</li>
              </ul>
            </div>
          </div>

          <div className="modal-footer" style={styles.footer}>
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              style={styles.cancelButton}
              disabled={isSubmitting}
            >
              Отмена
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              style={styles.saveButton}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Сохранение..." : "Сохранить изменения"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Вспомогательная функция для форматирования размера файла
function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

// Стили для модального окна (те же, что и раньше)
const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modal: {
    backgroundColor: "#fff",
    borderRadius: "8px",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
    width: "90%",
    maxWidth: "600px",
    maxHeight: "90vh",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "20px",
    borderBottom: "1px solid #e0e0e0",
    backgroundColor: "#f8f9fa",
  },
  title: {
    margin: 0,
    fontSize: "18px",
    fontWeight: "600",
    color: "#333",
  },
  closeButton: {
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: "8px",
    borderRadius: "4px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#666",
    transition: "background-color 0.2s",
  },
  body: {
    padding: "20px",
    overflowY: "auto",
    flex: 1,
  },
  error: {
    backgroundColor: "#fee",
    color: "#c33",
    padding: "12px",
    borderRadius: "4px",
    marginBottom: "16px",
    border: "1px solid #fcc",
  },
  formGroup: {
    marginBottom: "20px",
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontWeight: "500",
    color: "#333",
  },
  input: {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #ddd",
    borderRadius: "4px",
    fontSize: "14px",
    boxSizing: "border-box",
  },
  textarea: {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #ddd",
    borderRadius: "4px",
    fontSize: "14px",
    boxSizing: "border-box",
    resize: "vertical",
    fontFamily: "inherit",
  },
  hint: {
    fontSize: "12px",
    color: "#666",
    marginTop: "4px",
  },
  info: {
    marginTop: "24px",
    padding: "16px",
    backgroundColor: "#f8f9fa",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
  },
  infoTitle: {
    marginTop: 0,
    marginBottom: "12px",
    fontSize: "14px",
    color: "#555",
  },
  infoList: {
    margin: 0,
    paddingLeft: "20px",
    fontSize: "13px",
    color: "#666",
    lineHeight: "1.6",
  },
  footer: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "12px",
    padding: "20px",
    borderTop: "1px solid #e0e0e0",
    backgroundColor: "#f8f9fa",
  },
  cancelButton: {
    padding: "10px 20px",
    backgroundColor: "#6c757d",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    transition: "background-color 0.2s",
  },
  saveButton: {
    padding: "10px 24px",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    transition: "background-color 0.2s",
  },
}