"use client"

import { useState } from "react"
import type { FileItem } from "../types"
import FileActions from "./FileActions"
import { useAuth } from "../auth/AuthContext"

interface TreeNode {
  name: string
  type: "file" | "folder"
  file?: FileItem
  children: TreeNode[]
}

interface FileTreeNodeProps {
  node: TreeNode
  depth?: number
  onFileDeleted: () => void
  onFileUpdated: () => void
}

export default function FileTreeNode({ node, depth = 0, onFileDeleted, onFileUpdated }: FileTreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(depth < 1) // корень всегда раскрыт
  const { user } = useAuth()

  const handleToggle = () => {
    if (node.type === "folder") {
      setIsExpanded(!isExpanded)
    }
  }

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split(".").pop()?.toLowerCase()
    switch (ext) {
      case "pdf":
        return (
          <svg className="node-icon file-pdf" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        )
      case "jpg":
      case "jpeg":
      case "png":
      case "gif":
      case "svg":
      case "webp":
        return (
          <svg className="node-icon file-image" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        )
      case "js":
      case "ts":
      case "tsx":
      case "jsx":
      case "html":
      case "css":
      case "json":
      case "py":
      case "java":
        return (
          <svg className="node-icon file-code" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
        )
      case "zip":
      case "rar":
      case "tar":
      case "gz":
      case "7z":
        return (
          <svg className="node-icon file-archive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
          </svg>
        )
      default:
        return (
          <svg className="node-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        )
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("ru-RU", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className="tree-node">
      <div className={`tree-node-content ${node.type}`}>
        {node.type === "folder" ? (
          <>
            {depth > 0 && (
              <button onClick={handleToggle} className={`folder-toggle ${isExpanded ? "expanded" : ""}`}>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            )}
            <svg className="node-icon folder" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            <div className="node-info">
              <div className="node-name">{node.name}</div>
            </div>
            <span className="file-count">{node.children.length}</span>
          </>
        ) : (
          <>
            {getFileIcon(node.name)}
            <div className="node-info">
              <div className="node-name">{node.name}</div>
              {node.file?.comment && <div className="node-comment">{node.file.comment}</div>}
              {node.file && (
                <div className="node-details">
                  <div className="node-detail-item">
                    <strong>Размер:</strong> {formatFileSize(node.file.size)}
                  </div>
                  <div className="node-detail-item">
                    <strong>Расширение:</strong> {node.file.extension}
                  </div>
                  <div className="node-detail-item">
                    <strong>Создан:</strong> {formatDate(node.file.creation_date)}
                  </div>
                  {node.file.update_date && (
                    <div className="node-detail-item">
                      <strong>Изменён:</strong> {formatDate(node.file.update_date)}
                    </div>
                  )}
                </div>
              )}
            </div>
            {node.file && <FileActions file={node.file} onFileDeleted={onFileDeleted} onFileUpdated={onFileUpdated} />}
          </>
        )}
      </div>

      {node.type === "folder" && isExpanded && node.children.length > 0 && (
        <div className="tree-children">
          {node.children.map((child) => (
            <FileTreeNode
              key={child.name + Math.random()} // уникальный ключ для вложенных файлов
              node={child}
              depth={depth + 1}
              onFileDeleted={onFileDeleted}
              onFileUpdated={onFileUpdated}
            />
          ))}
        </div>
      )}
    </div>
  )
}
