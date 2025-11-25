"use client"

import type React from "react"

import { useState, useRef } from "react"
import { uploadFileWithProgress } from "../api/files"

interface UploadFileProps {
  onFileUploaded: () => void
}

export default function UploadFile({ onFileUploaded }: UploadFileProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [path, setPath] = useState("")
  const [comment, setComment] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      uploadFile(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadFile(file)
    }
  }

  const uploadFile = async (file: File) => {
    setIsUploading(true)
    setProgress(0)

    try {
      await uploadFileWithProgress(file, { path, comment }, (p) => setProgress(p * 100))

      onFileUploaded()
      setPath("")
      setComment("")
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    } catch (error) {
      console.error("Ошибка при загрузке:", error)
      alert("Не удалось загрузить файл")
    } finally {
      setIsUploading(false)
      setProgress(0)
    }
  }

  return (
    <div className="upload-container-compact">
      <h2 className="upload-title">Загрузка файла</h2>

      <div
        className={`upload-dropzone-compact ${isDragging ? "dragging" : ""} ${isUploading ? "uploading" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input ref={fileInputRef} type="file" onChange={handleFileSelect} className="hidden" disabled={isUploading} />

        {isUploading ? (
          <div className="upload-progress-compact">
            <svg className="upload-icon-compact" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="upload-text-compact">{Math.round(progress)}%</p>
            <div className="progress-bar-compact">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>
        ) : (
          <div className="upload-content-compact">
            <svg className="upload-icon-compact" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="upload-text-compact">Выберите или перетащите</p>
          </div>
        )}
      </div>

      {!isUploading && (
        <div className="upload-options-compact">
          <input
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="Путь (необязательно)"
            className="upload-input-compact"
          />
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Комментарий"
            className="upload-input-compact"
          />
        </div>
      )}
    </div>
  )
}
