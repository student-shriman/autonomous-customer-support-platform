"use client";

import React, { useState } from "react";
import { HITLAction } from "../lib/api";
import { 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Edit3, 
  FileText, 
  ArrowRight,
  ShieldAlert,
  Terminal
} from "lucide-react";

interface HITLActionCenterProps {
  hitlActions: HITLAction[];
  onReviewAction: (
    actionId: string, 
    decision: "APPROVED" | "MODIFIED" | "REJECTED", 
    notes: string, 
    modifiedPayload?: Record<string, any>
  ) => Promise<void>;
  onInspectTicket: (ticketId: string) => void;
}

export function HITLActionCenter({
  hitlActions,
  onReviewAction,
  onInspectTicket,
}: HITLActionCenterProps) {
  const [selectedActionId, setSelectedActionId] = useState<string | null>(
    hitlActions.length > 0 ? hitlActions[0].id : null
  );
  const [notes, setNotes] = useState<string>("");
  const [customAmount, setCustomAmount] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);

  const selectedAction = hitlActions.find((a) => a.id === selectedActionId) || hitlActions[0];

  const handleReview = async (decision: "APPROVED" | "MODIFIED" | "REJECTED") => {
    if (!selectedAction) return;
    setSubmitting(true);
    try {
      let modifiedPayload: Record<string, any> | undefined = undefined;
      if (decision === "MODIFIED" && customAmount) {
        modifiedPayload = {
          ...selectedAction.proposed_payload,
          amount: parseFloat(customAmount),
        };
      }
      await onReviewAction(selectedAction.id, decision, notes, modifiedPayload);
      setNotes("");
      setCustomAmount("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            <span>Human-in-the-Loop (HITL) Action Center</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Review and sign off on high-risk, sensitive, or financial agent mutation workflows.
          </p>
        </div>
        <div className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30">
          {hitlActions.length} Pending Approval
        </div>
      </div>

      {hitlActions.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 mx-auto flex items-center justify-center">
            <CheckCircle className="w-6 h-6" />
          </div>
          <h3 className="mt-4 text-base font-semibold text-white">All Clear! No High-Risk Actions Pending</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
            All safe operational actions are being autonomously executed by the LangGraph multi-agent pipeline.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Action List Sidebar */}
          <div className="space-y-3 lg:col-span-1">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-1">
              Review Queue
            </h3>
            {hitlActions.map((action) => (
              <div
                key={action.id}
                onClick={() => setSelectedActionId(action.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  (selectedAction && selectedAction.id === action.id)
                    ? "bg-slate-800 border-amber-500/50 shadow-md shadow-amber-500/10"
                    : "bg-slate-900 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-amber-400">{action.id}</span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">
                    {action.risk_level} Risk
                  </span>
                </div>
                <div className="font-medium text-white text-sm mt-2">{action.action_type}</div>
                <p className="text-xs text-slate-400 truncate mt-1">{action.risk_reason}</p>
                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-800">
                  <span>Ticket: {action.ticket_id}</span>
                  <span>{new Date(action.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Action Details & Operator Controls */}
          {selectedAction && (
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
              {/* Risk Alert Banner */}
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-amber-300">High-Risk Mutation Gated by Safety Policy</h4>
                  <p className="text-xs text-slate-300 mt-1">{selectedAction.risk_reason}</p>
                </div>
              </div>

              {/* Action Info */}
              <div className="grid grid-cols-2 gap-4 text-sm bg-slate-950 p-4 rounded-lg border border-slate-800">
                <div>
                  <span className="text-xs text-slate-500 block">Target Action</span>
                  <span className="font-mono font-semibold text-indigo-400">{selectedAction.action_type}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Associated Ticket</span>
                  <button
                    onClick={() => onInspectTicket(selectedAction.ticket_id)}
                    className="font-mono font-semibold text-slate-200 hover:text-indigo-400 inline-flex items-center space-x-1"
                  >
                    <span>{selectedAction.ticket_id}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {/* Proposed Payload */}
              <div>
                <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 mb-2">
                  <Terminal className="w-4 h-4 text-indigo-400" />
                  <span>PROPOSED OPERATIONAL PAYLOAD</span>
                </div>
                <pre className="bg-slate-950 border border-slate-800 rounded-lg p-4 text-xs font-mono text-emerald-300 overflow-x-auto">
                  {JSON.stringify(selectedAction.proposed_payload, null, 2)}
                </pre>
              </div>

              {/* Modify Controls */}
              {selectedAction.action_type === "issue_refund" && (
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Override Refund Amount (USD)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder={`Original amount: $${selectedAction.proposed_payload?.amount || 0}`}
                    value={customAmount}
                    onChange={(e) => setCustomAmount(e.target.value)}
                    className="w-full sm:w-64 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">Leave blank to approve original amount.</p>
                </div>
              )}

              {/* Operator Notes */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Specialist Review Notes & Compliance Justification
                </label>
                <textarea
                  rows={2}
                  placeholder="e.g. Verified duplicate Stripe checkout webhook transaction..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Decision Buttons */}
              <div className="flex flex-wrap items-center justify-end gap-3 pt-2 border-t border-slate-800">
                <button
                  disabled={submitting}
                  onClick={() => handleReview("REJECTED")}
                  className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-sm font-semibold transition-all disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject & Escalate</span>
                </button>

                {customAmount && (
                  <button
                    disabled={submitting}
                    onClick={() => handleReview("MODIFIED")}
                    className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold shadow-md shadow-amber-600/20 transition-all disabled:opacity-50"
                  >
                    <Edit3 className="w-4 h-4" />
                    <span>Apply Override & Execute</span>
                  </button>
                )}

                <button
                  disabled={submitting}
                  onClick={() => handleReview("APPROVED")}
                  className="inline-flex items-center space-x-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve & Execute</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
