"use client";

import React from "react";
import { Ticket, TicketMessage } from "../lib/api";
import { 
  X, 
  GitCommit, 
  CheckCircle2, 
  Clock, 
  Cpu, 
  ShieldAlert, 
  Search, 
  Wrench, 
  MessageSquare 
} from "lucide-react";

interface TraceFlowModalProps {
  ticket: Ticket;
  onClose: () => void;
}

export function TraceFlowModal({ ticket, onClose }: TraceFlowModalProps) {
  // Extract trace steps from recent agent messages
  const traceSteps: Array<{
    agent_name: string;
    action_type?: string;
    summary: string;
    details?: any;
    timestamp?: string;
  }> = [];

  if (ticket.messages) {
    for (const msg of ticket.messages) {
      if (msg.agent_trace && Array.isArray(msg.agent_trace)) {
        traceSteps.push(...msg.agent_trace);
      }
    }
  }

  const getAgentIcon = (name: string) => {
    if (name.includes("Supervisor")) return <Cpu className="w-4 h-4 text-violet-400" />;
    if (name.includes("Troubleshooting")) return <Wrench className="w-4 h-4 text-amber-400" />;
    if (name.includes("Knowledge")) return <Search className="w-4 h-4 text-sky-400" />;
    if (name.includes("Escalation")) return <ShieldAlert className="w-4 h-4 text-rose-400" />;
    return <MessageSquare className="w-4 h-4 text-emerald-400" />;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div>
            <div className="flex items-center space-x-2">
              <GitCommit className="w-5 h-5 text-indigo-400" />
              <h3 className="text-base font-bold text-white">
                Multi-Agent Execution Trace & Timeline
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Inspect step-by-step LangGraph agent transitions for Ticket {ticket.id}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Timeline Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {traceSteps.length === 0 ? (
            <div className="text-center py-10 text-slate-500">
              <Clock className="w-10 h-10 mx-auto text-slate-600 mb-2" />
              <p className="text-sm">No agent trace steps logged for this ticket yet.</p>
              <p className="text-xs text-slate-600 mt-1">Send a message to trigger agent execution.</p>
            </div>
          ) : (
            <div className="relative border-l-2 border-slate-800 ml-4 space-y-6">
              {traceSteps.map((step, idx) => (
                <div key={idx} className="relative pl-6">
                  {/* Step Marker */}
                  <div className="absolute -left-2.5 top-0.5 w-5 h-5 rounded-full bg-slate-900 border-2 border-indigo-500 flex items-center justify-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                  </div>

                  {/* Step Card */}
                  <div className="bg-slate-950 border border-slate-800/80 rounded-xl p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getAgentIcon(step.agent_name)}
                        <span className="text-xs font-bold text-white">{step.agent_name}</span>
                        {step.action_type && (
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            {step.action_type}
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">Step #{idx + 1}</span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed font-sans">{step.summary}</p>

                    {step.details && Object.keys(step.details).length > 0 && (
                      <details className="mt-2 text-[11px] font-mono text-slate-400 cursor-pointer">
                        <summary className="hover:text-slate-200 transition-colors">
                          Inspect Node Metadata & Tool Output
                        </summary>
                        <pre className="mt-2 bg-slate-900 border border-slate-800 rounded p-2 text-emerald-300 overflow-x-auto text-[10px]">
                          {JSON.stringify(step.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Total Steps: {traceSteps.length}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
