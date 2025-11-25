import type { FileItem } from "../types"
import FileTreeNode from "./FileTreeNode"
import "./FileTree.css"

interface FileTreeProps {
  files: FileItem[]
  onFileDeleted: () => void
  onFileUpdated: () => void
}

interface TreeNode {
  name: string
  path: string
  type: "file" | "folder"
  file?: FileItem
  children: TreeNode[]
}

function buildTree(files: FileItem[]): TreeNode {
  const root: TreeNode = {
    name: "root",
    path: "",
    type: "folder",
    children: [],
  }

  files.forEach((file) => {
    const pathParts = file.path.split("/").filter(Boolean)
    let currentNode = root

    pathParts.forEach((part, index) => {
      const isLastPart = index === pathParts.length - 1

      if (isLastPart) {
        // Это файл
        currentNode.children.push({
          name: part,
          path: file.path,
          type: "file",
          file: file,
          children: [],
        })
      } else {
        // Это папка
        let folder = currentNode.children.find((child) => child.name === part && child.type === "folder")

        if (!folder) {
          folder = {
            name: part,
            path: pathParts.slice(0, index + 1).join("/"),
            type: "folder",
            children: [],
          }
          currentNode.children.push(folder)
        }

        currentNode = folder
      }
    })
  })

  // Сортировка: папки первые, потом файлы, алфавитно
  const sortNodes = (nodes: TreeNode[]) => {
    nodes.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === "folder" ? -1 : 1
      }
      return a.name.localeCompare(b.name)
    })
    nodes.forEach((node) => {
      if (node.children.length > 0) {
        sortNodes(node.children)
      }
    })
  }

  sortNodes(root.children)

  return root
}

export default function FileTree({ files, onFileDeleted, onFileUpdated }: FileTreeProps) {
  const tree = buildTree(files)

  if (files.length === 0) {
    return (
      <div className="file-tree-empty">
        <p>Нет файлов в хранилище</p>
      </div>
    )
  }

  return (
    <div className="file-tree-container">
      {tree.children.map((node) => (
        <FileTreeNode key={node.path} node={node} onFileDeleted={onFileDeleted} onFileUpdated={onFileUpdated} />
      ))}
    </div>
  )
}
