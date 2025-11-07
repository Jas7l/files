export type FileItem = {
  id: number;
  name: string;
  extension: string;
  size: number;
  path: string;
  comment: string | null;
  creation_date: string;
  update_date: string | null;
};
