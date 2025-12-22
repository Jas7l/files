import type { FileItem } from "../types";
import FileTreeNode from "./FileTreeNode";
import "./FileTree.css";
import { useAuth } from "../auth/AuthContext";

interface FileTreeProps {
  files: FileItem[];
  onFileDeleted: () => void;
  onFileUpdated: () => void;
}

interface TreeNode {
  name: string;
  type: "file" | "folder";
  file?: FileItem;
  children: TreeNode[];
}

function buildTree(files: FileItem[], username: string): TreeNode {
  const root: TreeNode = {
    name: `Диск ${username}`,
    type: "folder",
    children: [],
  };

  files.forEach((file) => {
    const pathParts = file.relative_path
      ? file.relative_path.split("/").filter(Boolean)
      : [];

    let currentNode = root;

    // создаем все папки по relative_path
    pathParts.forEach((part) => {
      let folder = currentNode.children.find(
        (child) => child.name === part && child.type === "folder"
      );

      if (!folder) {
        folder = { name: part, type: "folder", children: [] };
        currentNode.children.push(folder);
      }

      currentNode = folder;
    });

    // добавляем файл в последнюю папку
    currentNode.children.push({
      name: file.name,
      type: "file",
      file,
      children: [],
    });
  });

  const sortNodes = (nodes: TreeNode[]) => {
    nodes.sort((a, b) => {
      if (a.type !== b.type) return a.type === "folder" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    nodes.forEach((node) => node.children && sortNodes(node.children));
  };

  sortNodes(root.children);
  return root;
}

export default function FileTree({ files, onFileDeleted, onFileUpdated }: FileTreeProps) {
  const { user } = useAuth();
  const tree = user ? buildTree(files, user.username) : null;

  if (!tree || files.length === 0) {
    return (
      <div className="file-tree-empty">
        <p>Нет файлов в хранилище</p>
      </div>
    );
  }

  return (
    <div className="file-tree-container">
      <FileTreeNode node={tree} depth={0} onFileDeleted={onFileDeleted} onFileUpdated={onFileUpdated} />
    </div>
  );
}
