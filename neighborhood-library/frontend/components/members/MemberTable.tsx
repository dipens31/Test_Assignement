import { Users, Pencil, List, Copy, Check } from "lucide-react";
import type { Member } from "@/lib/types";
import { useToast } from "@/components/ui/Toast";
import { useState } from "react";

interface MemberTableProps {
  members: Member[];
  onEdit?: (member: Member) => void;
  onViewLoans?: (member: Member) => void;
}

export default function MemberTable({ members, onEdit, onViewLoans }: MemberTableProps) {
  const { toast } = useToast();
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyId = async (id: string) => {
    await navigator.clipboard.writeText(id);
    setCopiedId(id);
    toast("success", "Member ID copied to clipboard");
    setTimeout(() => setCopiedId(null), 2000);
  };
  if (members.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
        <Users className="w-10 h-10 text-slate-300" />
        <p className="font-medium">No members found</p>
        <p className="text-sm">Register a member to get started.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {members.map((member) => (
            <tr key={member.id}>
              <td>
                <button
                  onClick={() => copyId(member.id)}
                  className="inline-flex items-center gap-1 text-xs font-mono text-slate-500 hover:text-brand-600 transition-colors group"
                  title="Copy Member ID"
                >
                  <span className="truncate max-w-[100px]">{member.id.slice(0, 8)}...</span>
                  {copiedId === member.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100" />}
                </button>
              </td>
              <td>
                <span className="font-semibold text-slate-900">{member.name}</span>
              </td>
              <td className="text-slate-600">{member.email}</td>
              <td className="text-slate-400">{member.phone ?? "—"}</td>
              <td className="text-slate-400 max-w-[200px] truncate" title={member.address ?? ""}>{member.address ?? "—"}</td>
              <td className="text-right pr-4">
                <div className="flex items-center justify-end gap-1">
                  {onViewLoans && (
                    <button onClick={() => onViewLoans(member)} className="btn-ghost btn-sm inline-flex items-center gap-1">
                      <List className="w-3.5 h-3.5" /> Loans
                    </button>
                  )}
                  {onEdit && (
                    <button onClick={() => onEdit(member)} className="btn-ghost btn-sm inline-flex items-center gap-1">
                      <Pencil className="w-3.5 h-3.5" /> Edit
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
