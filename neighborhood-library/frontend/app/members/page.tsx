"use client";

import { useEffect, useState } from "react";
import { membersApi } from "@/lib/api/members";
import type { Member, MemberCreatePayload } from "@/lib/types";
import MemberTable from "@/components/members/MemberTable";
import MemberForm from "@/components/members/MemberForm";
import Modal from "@/components/ui/Modal";
import Alert from "@/components/ui/Alert";
import { SkeletonTable } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import LoanTable from "@/components/loans/LoanTable";
import type { Loan } from "@/lib/types";
import { Plus, Search, X } from "lucide-react";

export default function MembersPage() {
  const { toast } = useToast();
  const [members, setMembers] = useState<Member[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [editMember, setEditMember] = useState<Member | null>(null);
  const [viewLoans, setViewLoans] = useState<{ member: Member; loans: Loan[] } | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const limit = 5;

  const fetchMembers = async () => {
    setLoading(true); setError("");
    try {
      const data = await membersApi.list({ skip: page * limit, limit, name: search || undefined });
      setMembers(data.items); setTotal(data.total);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load members.");
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchMembers(); }, [search, page]);

  const handleCreate = async (data: MemberCreatePayload) => {
    await membersApi.create(data);
    setShowAdd(false);
    toast("success", "Member registered successfully.");
    fetchMembers();
  };

  const handleUpdate = async (data: MemberCreatePayload) => {
    if (!editMember) return;
    await membersApi.update(editMember.id, data);
    setEditMember(null);
    toast("success", "Member updated successfully.");
    fetchMembers();
  };

  const handleViewLoans = async (member: Member) => {
    try {
      const loans = await membersApi.loans(member.id);
      setViewLoans({ member, loans });
    } catch {
      toast("error", "Could not load loans for this member.");
    }
  };

  const totalPages = Math.ceil(total / limit);
  const canPrev = page > 0;
  const canNext = page < totalPages - 1;

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Members</h1>
          <p className="page-subtitle">{loading ? "Loading…" : `${total} registered member${total !== 1 ? "s" : ""}`}</p>
        </div>
        <button className="btn-primary" onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" /> Register Member
        </button>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          <input className="input pl-9 w-64" placeholder="Search by name…" value={search} onChange={(e) => setSearch(e.target.value)} />
          {search && <button onClick={() => setSearch("")} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"><X className="w-3.5 h-3.5" /></button>}
        </div>
      </div>

      {error && <Alert variant="error" message={error} onClose={() => setError("")} />}
      {loading ? <SkeletonTable rows={5} cols={5} /> : <MemberTable members={members} onEdit={setEditMember} onViewLoans={handleViewLoans} />}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Showing {page * limit + 1}-{Math.min((page + 1) * limit, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={!canPrev}
              className="btn-ghost btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-sm text-slate-600">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={!canNext}
              className="btn-ghost btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {showAdd && (
        <Modal title="Register New Member" onClose={() => setShowAdd(false)}>
          <MemberForm onSubmit={handleCreate} onCancel={() => setShowAdd(false)} submitLabel="Register" />
        </Modal>
      )}
      {editMember && (
        <Modal title="Edit Member" onClose={() => setEditMember(null)}>
          <MemberForm initial={editMember} onSubmit={handleUpdate} onCancel={() => setEditMember(null)} submitLabel="Save Changes" />
        </Modal>
      )}
      {viewLoans && (
        <Modal title={`Loans — ${viewLoans.member.name}`} onClose={() => setViewLoans(null)} size="lg">
          <LoanTable loans={viewLoans.loans} showFine />
        </Modal>
      )}
    </div>
  );
}
