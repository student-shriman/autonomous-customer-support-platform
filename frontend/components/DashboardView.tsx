"use client";

import React, { useState } from "react";
import { Ticket } from "../lib/api";
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Activity, 
  ArrowRight, 
  Filter, 
  Search,
  PlusCircle,
  FileText
} from "lucide-react";

interface DashboardViewProps {
  tickets: Ticket[];
  pendingHitlCount: number;
  onSelectTicket: (ticket: Ticket) => void;
  onCreateTicket: (title: string, message: string, severity: string) => Promise<void>;
}

export function DashboardView({
  tickets,
  pendingHitlCount,
  onSelectTicket,
  onCreateTicket,
}: DashboardViewProps) {
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>("");
  const [newMessage, setNewMessage] = useState<string>("");
  const [newSeverity, setNewSeverity] = useState<string>("P1");
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Filter tickets
  const filteredTickets = tickets.filter((t) => {
    if (severityFilter !== "ALL" && t.severity !== severityFilter) return false;
    if (statusFilter !== "ALL" && t.status !== statusFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        t.title.toLowerCase().includes(q) ||
        t.id.toLowerCase().includes(q) ||
        (t.intent && t.intent.toLowerCase().includes(q))
      );
    }
    return true;
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newMessage) return;
    setSubmitting(true);
    try {
      await onCreateTicket(newTitle, newMessage, newSeverity);
      setShowCreateModal(false);
      setNewTitle("");
      setNewMessage("");
    } finally {
      setSubmitting(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "P0":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">P0 Outage</span>;
      case "P1":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">P1 Financial</span>;
      case "P2":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">P2 Feature</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-500/20 text-slate-300 border border-slate-500/30">P3 Minor</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending_hitl":
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">Pending HITL</span>;
      case "investigating":
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/30">Investigating</span>;
      case "resolved":
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Resolved</span>;
      case "escalated":
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/30">Escalated</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/30">Open</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* KPI Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Total Tickets</span>
            <FileText className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">{tickets.length}</div>
          <div className="mt-1 text-xs text-slate-500">Live in Neon PostgreSQL</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">HITL Gated Actions</span>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-amber-400">{pendingHitlCount}</div>
          <div className="mt-1 text-xs text-slate-500">Awaiting Specialist Sign-off</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Auto-Resolution Rate</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-emerald-400">84.2%</div>
          <div className="mt-1 text-xs text-slate-500">Resolved autonomously</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Model Response</span>
            <Activity className="w-5 h-5 text-violet-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-violet-400">1.8s</div>
          <div className="mt-1 text-xs text-slate-500">gpt-6-luna TTFT average</div>
        </div>
      </div>

      {/* Triage Header & Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Active Ticket Triage Feed</h2>
            <p className="text-xs text-slate-400">Monitor incoming customer requests, priority ratings, and multi-agent execution status.</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-md shadow-indigo-600/20 transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Simulate Customer Ticket</span>
          </button>
        </div>

        {/* Search & Severity Filter Bar */}
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by ticket ID, title, or intent..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center space-x-1.5 bg-slate-950 border border-slate-800 rounded-lg p-1">
            {["ALL", "P0", "P1", "P2", "P3"].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                  severityFilter === sev
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* Tickets Table */}
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-slate-400 text-xs uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4">Title & Intent</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Created</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No tickets match the selected filters.
                  </td>
                </tr>
              ) : (
                filteredTickets.map((ticket) => (
                  <tr key={ticket.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-indigo-400">
                      {ticket.id}
                    </td>
                    <td className="py-3.5 px-4 max-w-md">
                      <div className="font-medium text-white truncate">{ticket.title}</div>
                      {ticket.intent && (
                        <div className="text-xs text-slate-400 truncate mt-0.5">{ticket.intent}</div>
                      )}
                    </td>
                    <td className="py-3.5 px-4">{getSeverityBadge(ticket.severity)}</td>
                    <td className="py-3.5 px-4">{getStatusBadge(ticket.status)}</td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                      {new Date(ticket.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => onSelectTicket(ticket)}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Simulate Customer Ticket */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Create Support Ticket</h3>
            <p className="text-xs text-slate-400 mt-1">
              Simulate an incoming customer request to trigger the 6-agent LangGraph pipeline.
            </p>

            <form onSubmit={handleCreate} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Ticket Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Duplicate charge on monthly renewal invoice"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Severity Target</label>
                <select
                  value={newSeverity}
                  onChange={(e) => setNewSeverity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="P0">P0 - Outage / Emergency</option>
                  <option value="P1">P1 - Financial / Billing Dispute</option>
                  <option value="P2">P2 - Feature / Technical Issue</option>
                  <option value="P3">P3 - Minor / Guidance Inquiry</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Customer Message</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Describe the problem from the customer's point of view..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-md shadow-indigo-600/20 disabled:opacity-50"
                >
                  {submitting ? "Submitting..." : "Dispatch to Agents"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
