"use client";

import React, { useState, useEffect, useRef } from "react";
import { Ticket, TicketMessage, sendChatMessage } from "../lib/api";
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  BookOpen, 
  Clock, 
  ShieldAlert, 
  CheckCircle,
  HelpCircle
} from "lucide-react";

interface CustomerPortalViewProps {
  tickets: Ticket[];
  selectedTicket: Ticket | null;
  onSelectTicket: (ticket: Ticket) => void;
  onRefreshTickets: () => void;
}

export function CustomerPortalView({
  tickets,
  selectedTicket,
  onSelectTicket,
  onRefreshTickets,
}: CustomerPortalViewProps) {
  const [messages, setMessages] = useState<TicketMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [sending, setSending] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Set active ticket to first if none selected
  const currentTicket = selectedTicket || (tickets.length > 0 ? tickets[0] : null);

  useEffect(() => {
    if (currentTicket && currentTicket.messages) {
      setMessages(currentTicket.messages);
    } else {
      setMessages([]);
    }
  }, [currentTicket]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !currentTicket) return;

    const userText = inputMessage.trim();
    setInputMessage("");
    setSending(true);

    // Optimistic UI message
    const tempUserMsg: TicketMessage = {
      id: "temp-" + Date.now(),
      ticket_id: currentTicket.id,
      sender_type: "customer",
      sender_name: "You",
      content: userText,
      citations: [],
      agent_trace: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await sendChatMessage(currentTicket.id, userText);
      const agentMsg: TicketMessage = {
        id: "agent-" + Date.now(),
        ticket_id: currentTicket.id,
        sender_type: "agent",
        sender_name: "Autonomous Support Agent",
        content: res.reply,
        citations: res.citations || [],
        agent_trace: res.agent_trace || [],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, agentMsg]);
      onRefreshTickets();
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[720px]">
      {/* Ticket Selector Sidebar */}
      <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col h-full">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 px-1">
          Your Support Sessions
        </h3>
        <div className="space-y-2 overflow-y-auto flex-1 pr-1">
          {tickets.length === 0 ? (
            <div className="text-xs text-slate-500 text-center py-6">No support sessions active.</div>
          ) : (
            tickets.map((t) => (
              <div
                key={t.id}
                onClick={() => onSelectTicket(t)}
                className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                  currentTicket && currentTicket.id === t.id
                    ? "bg-indigo-600/10 border-indigo-500/40 text-white"
                    : "bg-slate-950/60 border-slate-800/80 text-slate-400 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-bold text-indigo-400">{t.id}</span>
                  <span className="uppercase text-[10px] font-bold px-1.5 py-0.2 rounded bg-slate-800">
                    {t.severity}
                  </span>
                </div>
                <div className="text-xs font-medium text-slate-200 truncate mt-1">{t.title}</div>
                <div className="text-[10px] text-slate-500 mt-1">
                  Status: <span className="text-slate-400 capitalize">{t.status.replace("_", " ")}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl flex flex-col h-full overflow-hidden shadow-xl">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold text-white">
                  {currentTicket ? currentTicket.title : "Live Support Chat"}
                </span>
                {currentTicket && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    {currentTicket.id}
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Powered by gpt-6-luna & Pinecone Hybrid RAG</span>
              </div>
            </div>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
              <HelpCircle className="w-10 h-10 text-slate-600" />
              <p className="text-sm">Start your conversation with the Autonomous Support Agent.</p>
              <p className="text-xs text-slate-600">The agent will investigate, retrieve relevant manuals, and resolve your issue.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start space-x-3 ${
                  msg.sender_type === "customer" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.sender_type !== "customer" && (
                  <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-xl rounded-2xl p-4 text-sm ${
                    msg.sender_type === "customer"
                      ? "bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20"
                      : "bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none shadow-sm"
                  }`}
                >
                  <div className="text-[11px] font-semibold mb-1 opacity-75">
                    {msg.sender_name}
                  </div>
                  <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>

                  {/* Cited Grounding Documents */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center space-x-1 mb-1.5">
                        <BookOpen className="w-3 h-3" />
                        <span>Cited Reference Documentation</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.citations.map((cite, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] bg-slate-900 border border-slate-700/80 text-slate-300"
                          >
                            <span>📄</span>
                            <span className="font-medium">{cite.title}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.sender_type === "customer" && (
                  <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {sending && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-950 border border-slate-800 rounded-2xl rounded-bl-none p-4 text-xs text-slate-400 flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
                <span>LangGraph multi-agent loop executing (Investigate & Retrieve)...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Bar */}
        <form onSubmit={handleSend} className="p-4 bg-slate-950/60 border-t border-slate-800 flex items-center space-x-3">
          <input
            type="text"
            disabled={sending || !currentTicket}
            placeholder={currentTicket ? "Type your message or inquiry..." : "Select a ticket first"}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={sending || !inputMessage.trim() || !currentTicket}
            className="w-11 h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shadow-lg shadow-indigo-600/20 disabled:opacity-50 transition-all shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
