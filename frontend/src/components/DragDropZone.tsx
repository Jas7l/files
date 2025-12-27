"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { uploadFileWithProgress } from "../api/files"

interface DragDropZoneProps {
  onFileUploaded: () => void
  children: React.ReactNode
}

interface UploadModalProps {
  file: File
  onClose: () => void
  onUpload: (path: string, comment: string) => Promise<void>
}

function UploadModal({ file, onClose, onUpload }: UploadModalProps) {
  const [path, setPath] = useState("")
  const [comment, setComment] = useState("")
  const [isUploading, setIsUploading] = useState(false)

  const handleUpload = async () => {
    if (isUploading) return
    setIsUploading(true)
    try {
      await onUpload(path, comment)
      onClose()
    } catch (error) {
      console.error("Ошибка при загрузке:", error)
      alert("Не удалось загрузить файл")
    } finally {
      setIsUploading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  return (
    <div className="modal-overlay" onKeyDown={handleKeyDown}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Загрузка файла</h3>
          <button onClick={onClose} className="modal-close-btn">
            ×
          </button>
        </div>
        <div className="modal-body">
          <div className="file-info">
            <div className="file-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div className="file-details">
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="path">Путь (необязательно)</label>
            <input
              id="path"
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="Например: documents/work"
              className="form-input"
            />
            <small className="form-help">Относительный путь, где будет сохранен файл</small>
          </div>

          <div className="form-group">
            <label htmlFor="comment">Комментарий (необязательно)</label>
            <input
              id="comment"
              type="text"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Описание файла"
              className="form-input"
            />
          </div>
        </div>
        <div className="modal-footer">
          <button onClick={onClose} className="btn-secondary" disabled={isUploading}>
            Отмена
          </button>
          <button onClick={handleUpload} className="btn-primary" disabled={isUploading}>
            {isUploading ? (
              <>
                <span className="spinner"></span>
                Загрузка...
              </>
            ) : (
              "Загрузить"
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function DragDropZone({ children, onFileUploaded }: DragDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const dragCounter = useRef(0)
  const dropZoneRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleDragOverGlobal = (e: DragEvent) => {
      e.preventDefault()
    }

    document.addEventListener("dragover", handleDragOverGlobal)
    document.addEventListener("drop", handleDragOverGlobal)

    return () => {
      document.removeEventListener("dragover", handleDragOverGlobal)
      document.removeEventListener("drop", handleDragOverGlobal)
    }
  }, [])

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Увеличиваем счетчик при каждом входе в зону
    dragCounter.current++

    // Устанавливаем состояние драга только если мы вошли в основную зону
    if (e.currentTarget === e.target) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Уменьшаем счетчик при каждом выходе из зоны
    dragCounter.current--

    // Снимаем состояние драга только когда полностью вышли из зоны
    if (dragCounter.current === 0) {
      setIsDragging(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Подсвечиваем зону при перетаскивании
    if (!isDragging) {
      setIsDragging(true)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Сбрасываем счетчик
    dragCounter.current = 0
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      const file = files[0]
      setSelectedFile(file)
    }
  }

  const handleUpload = async (path: string, comment: string) => {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      await uploadFileWithProgress(
        selectedFile,
        { path, comment },
        (progress) => setUploadProgress(progress * 100)
      )

      setSelectedFile(null)
      onFileUploaded()
    } catch (error) {
      console.error("Ошибка при загрузке:", error)
      throw error
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const handleCloseModal = () => {
    if (!isUploading) {
      setSelectedFile(null)
    }
  }

  return (
    <>
      <div
        ref={dropZoneRef}
        className={`drag-drop-zone ${isDragging ? "dragging" : ""}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        style={{ width: '100%', height: '100%' }}
      >
        {children}

        {isDragging && (
          <div className="drop-overlay">
            <div className="drop-content">
              <svg className="drop-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="drop-text">Отпустите файл для загрузки</p>
            </div>
          </div>
        )}
      </div>

      {selectedFile && (
        <UploadModal
          file={selectedFile}
          onClose={handleCloseModal}
          onUpload={handleUpload}
        />
      )}

      <style jsx>{`
        .drag-drop-zone {
          position: relative;
          width: 100%;
          height: 100%;
          min-height: 400px;
          box-sizing: border-box;
        }

        .drag-drop-zone.dragging {
          outline: 2px dashed #4f46e5;
          outline-offset: -2px;
          background-color: rgba(79, 70, 229, 0.05);
        }

        .drop-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10;
          border-radius: 8px;
          pointer-events: none;
        }

        .drop-content {
          text-align: center;
          padding: 40px;
          border-radius: 16px;
          background: white;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
          border: 3px dashed #4f46e5;
          animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            border-color: #4f46e5;
          }
          50% {
            transform: scale(1.02);
            border-color: #6366f1;
          }
        }

        .drop-icon {
          width: 72px;
          height: 72px;
          color: #4f46e5;
          margin-bottom: 20px;
        }

        .drop-text {
          font-size: 20px;
          font-weight: 600;
          color: #4f46e5;
          margin: 0;
        }

        /* Modal styles - улучшенные */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .modal-content {
          background: white;
          border-radius: 16px;
          width: 100%;
          max-width: 480px;
          max-height: 80vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
          overflow: hidden;
        }

        .modal-header {
          padding: 24px;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          justify-content: space-between;
          background-color: #f8fafc;
          flex-shrink: 0;
        }

        .modal-header h3 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
          color: #1f2937;
        }

        .modal-close-btn {
          background: none;
          border: none;
          font-size: 28px;
          cursor: pointer;
          color: #6b7280;
          padding: 4px 12px;
          border-radius: 6px;
          line-height: 1;
          transition: all 0.2s ease;
        }

        .modal-close-btn:hover {
          background-color: #e5e7eb;
          color: #1f2937;
        }

        .modal-body {
          padding: 24px;
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .file-info {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
          background-color: #f0f9ff;
          border-radius: 12px;
          border: 1px solid #e0f2fe;
        }

        .file-icon {
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #4f46e5, #6366f1);
          color: white;
          border-radius: 12px;
          flex-shrink: 0;
        }

        .file-details {
          flex: 1;
          min-width: 0;
        }

        .file-name {
          margin: 0 0 6px 0;
          font-weight: 600;
          color: #1f2937;
          font-size: 16px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .file-size {
          margin: 0;
          font-size: 14px;
          color: #6b7280;
        }

        .form-group {
          margin-bottom: 0;
        }

        .form-group label {
          display: block;
          margin-bottom: 10px;
          font-weight: 500;
          color: #374151;
          font-size: 15px;
        }

        .form-input {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid #e5e7eb;
          border-radius: 10px;
          font-size: 15px;
          transition: all 0.2s ease;
          box-sizing: border-box;
        }

        .form-input:focus {
          outline: none;
          border-color: #4f46e5;
          box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15);
        }

        .form-input::placeholder {
          color: #9ca3af;
        }

        .form-help {
          display: block;
          margin-top: 8px;
          font-size: 13px;
          color: #6b7280;
          line-height: 1.4;
        }

        .modal-footer {
          padding: 20px 24px;
          border-top: 1px solid #e5e7eb;
          display: flex;
          justify-content: flex-end;
          gap: 16px;
          background-color: #f8fafc;
          flex-shrink: 0;
        }

        .btn-primary,
        .btn-secondary {
          padding: 12px 28px;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          border: none;
          min-width: 100px;
        }

        .btn-primary {
          background: linear-gradient(135deg, #4f46e5, #6366f1);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: linear-gradient(135deg, #4338ca, #4f46e5);
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }

        .btn-primary:active:not(:disabled) {
          transform: translateY(0);
        }

        .btn-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .btn-secondary {
          background-color: #f3f4f6;
          color: #374151;
        }

        .btn-secondary:hover:not(:disabled) {
          background-color: #e5e7eb;
          transform: translateY(-1px);
        }

        .btn-secondary:active:not(:disabled) {
          transform: translateY(0);
        }

        .btn-secondary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .spinner {
          display: inline-block;
          width: 18px;
          height: 18px;
          margin-right: 10px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: spin 1s ease-in-out infinite;
          vertical-align: middle;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </>
  )
}