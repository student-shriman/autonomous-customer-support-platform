"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  Ticket, 
  HITLAction, 
  fetchTickets, 
  fetchHITLQueue, 
  createTicket, 
  reviewHITLAction 
} from "../lib/api";
import { Navbar } from "../components/Navbar";
import { DashboardView } from "../components/DashboardView";
import { HITLActionCenter } from "../components/HITLActionCenter";
import { CustomerPortalView } from "../components/CustomerPortalView";
import { TraceFlowModal } from "../components/TraceFlowModal";
import { RefreshCw, CheckCircle, AlertCircle } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "hitl" | "customer">("dashboard");
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [hitlActions, setHitlActions] = useState<HITLAction[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [inspectingTicket, setInspectingTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [tList, hList] = await Promise.all([
        fetchTickets(),
        fetchHITLQueue()
      ]);
      setTickets(tList);
      setHitlActions(hList);
    } catch (err) {
      console.error("Failed to load platform data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // 10s auto-refresh interval for live dashboard status
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [loadData]);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleCreateTicket = async (title: string, message: string, severity: string) => {
    try {
      const newTicket = await createTicket(title, message, severity);
      showToast(`Ticket ${newTicket.id} created and dispatched to agents!`);
      await loadData();
      setSelectedTicket(newTicket);
      setActiveTab("customer");
    } catch (err) {
      showToast("Failed to create ticket: " + String(err), "error");
    }
  };

  const handleReviewAction = async (
    actionId: string,
    decision: "APPROVED" | "MODIFIED" | "REJECTED",
    notes: string,
    modifiedPayload?: Record<string, any>
  ) => {
    try {
      await reviewHITLAction(actionId, decision, notes, modifiedPayload);
      showToast(`Action ${actionId} successfully ${decision.toLowerCase()}!`);
      await loadData();
    } catch (err) {
      showToast("Review submission error: " + String(err), "error");
    }
  };

  const handleInspectTicketFromHITL = (ticketId: string) => {
    const t = tickets.find((item) => item.id === ticketId);
    if (t) {
      setInspectingTicket(t);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingHitlCount={hitlActions.length}
      />

      {/* Floating Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div
            className={`px-4 py-3 rounded-xl shadow-2xl flex items-center space-x-2 text-sm font-semibold border ${
              notification.type === "success"
                ? "bg-emerald-950 text-emerald-200 border-emerald-500/40"
                : "bg-rose-950 text-rose-200 border-rose-500/40"
            }`}
          >
            {notification.type === "success" ? (
              <CheckCircle className="w-5 h-5 text-emerald-400" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-400" />
            )}
            <span>{notification.message}</span>
          </div>
        </div>
      )}

      {/* Main View Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="h-64 flex flex-col items-center justify-center space-y-3">
            <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
            <p className="text-sm text-slate-400">Connecting to Neon PostgreSQL & LangGraph Core...</p>
          </div>
        ) : (
          <>
            {activeTab === "dashboard" && (
              <DashboardView
                tickets={tickets}
                pendingHitlCount={hitlActions.length}
                onSelectTicket={(t) => setInspectingTicket(t)}
                onCreateTicket={handleCreateTicket}
              />
            )}

            {activeTab === "hitl" && (
              <HITLActionCenter
                hitlActions={hitlActions}
                onReviewAction={handleReviewAction}
                onInspectTicket={handleInspectTicketFromHITL}
              />
            )}

            {activeTab === "customer" && (
              <CustomerPortalView
                tickets={tickets}
                selectedTicket={selectedTicket}
                onSelectTicket={(t) => setSelectedTicket(t)}
                onRefreshTickets={loadData}
              />
            )}
          </>
        )}
      </main>

      {/* Trace Timeline Modal */}
      {inspectingTicket && (
        <TraceFlowModal
          ticket={inspectingTicket}
          onClose={() => setInspectingTicket(null)}
        />
      )}
    </div>
  );
}
