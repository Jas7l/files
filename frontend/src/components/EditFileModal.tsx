"use client"

import type React from "react"
import { useState } from "react"
import type { FileItem } from "../types"

interface EditFileModalProps {
  file: FileItem
  onClose: () => void
  onFileUpdated: () => void
}

export default function EditFileModal({ file, onClose, onFileUpdated }: EditFileModalProps) {
  const [comment, setComment] = useState(file.comment || "")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const formData = new FormData()
      formData.append("comment", comment)

      const response = await fetch(`http://localhost:8020/api/files/${file.id}`, {
        method: "PATCH",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Ошибка при обновлении файла")
      }

      onFileUpdated()
      onClose()
    } catch (error) {
      console.error("Ошибка при обновлении:", error)
      alert("Не удалось обновить файл")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">Редактировать комментарий</h2>
          <button onClick={onClose} className="modal-close">
            <svg className="modal-close-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">Имя файла</label>
              <div className="form-readonly">{file.name}</div>
            </div>

            <div className="form-group">
              <label className="form-label">Комментарий</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="form-textarea"
                rows={4}
                placeholder="Добавьте комментарий к файлу..."
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary" disabled={isSubmitting}>
              Отмена
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? "Сохранение..." : "Сохранить"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
