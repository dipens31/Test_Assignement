import { Copy, Check } from "lucide-react";
import { useState } from "react";
import { useToast } from "./Toast";

export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T, index: number) => React.ReactNode;
  className?: string;
  headerClassName?: string;
}

export interface Action<T> {
  label: string;
  icon?: React.ReactNode;
  onClick: (item: T) => void;
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  actions?: Action<T>[];
  emptyMessage?: string;
  emptyIcon?: React.ReactNode;
  emptyDescription?: string;
  idKey?: keyof T | string;
  showCopyId?: boolean;
}

export default function DataTable<T>({
  data,
  columns,
  actions,
  emptyMessage = "No items found",
  emptyIcon,
  emptyDescription,
  idKey = "id" as keyof T,
  showCopyId = true,
}: DataTableProps<T>) {
  const { toast } = useToast();
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyId = async (id: string) => {
    await navigator.clipboard.writeText(id);
    setCopiedId(id);
    toast("success", "ID copied to clipboard");
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
        {emptyIcon}
        <p className="font-medium">{emptyMessage}</p>
        {emptyDescription && <p className="text-sm">{emptyDescription}</p>}
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            {showCopyId && <th>ID</th>}
            {columns.map((column) => (
              <th key={String(column.key)} className={column.headerClassName}>
                {column.header}
              </th>
            ))}
            {actions && actions.length > 0 && <th />}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={String((item as any)[idKey])}>
              {showCopyId && (
                <td>
                  <button
                    onClick={() => copyId(String((item as any)[idKey]))}
                    className="inline-flex items-center gap-1 text-xs font-mono text-slate-500 hover:text-brand-600 transition-colors group"
                    title="Copy ID"
                  >
                    <span className="truncate max-w-[100px]">
                      {String((item as any)[idKey]).slice(0, 8)}...
                    </span>
                    {copiedId === String((item as any)[idKey]) ? (
                      <Check className="w-3.5 h-3.5 text-emerald-500" />
                    ) : (
                      <Copy className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100" />
                    )}
                  </button>
                </td>
              )}
              {columns.map((column) => (
                <td key={String(column.key)} className={column.className}>
                  {column.render ? column.render(item, index) : String((item as any)[column.key])}
                </td>
              ))}
              {actions && actions.length > 0 && (
                <td className="text-right pr-4">
                  <div className="flex items-center justify-end gap-1">
                    {actions.map((action, actionIndex) => (
                      <button
                        key={actionIndex}
                        onClick={() => action.onClick(item)}
                        className={action.className || "btn-ghost btn-sm inline-flex items-center gap-1"}
                      >
                        {action.icon}
                        {action.label}
                      </button>
                    ))}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
