"use client";

import React from "react";
import { ShieldCheck, AlertCircle, Bot, LifeBuoy, User } from "lucide-react";

interface NavbarProps {
  activeTab: "dashboard" | "hitl" | "customer";
  setActiveTab: (tab: "dashboard" | "hitl" | "customer") => void;
  pendingHitlCount: number;
}

export function Navbar({ activeTab, setActiveTab, pendingHitlCount }: NavbarProps) {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab("dashboard")}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white text-lg tracking-tight">CloudScale</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 font-semibold border border-indigo-500/20">
                Autonomous Support
              </span>
            </div>
            <p className="text-xs text-slate-400">Multi-Agent Customer Resolution Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === "dashboard"
                ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                : "text-slate-300 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            Support Ops Dashboard
          </button>

          <button
            onClick={() => setActiveTab("hitl")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all relative flex items-center space-x-1.5 ${
              activeTab === "hitl"
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                : "text-slate-300 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <span>HITL Action Center</span>
            {pendingHitlCount > 0 && (
              <span className="inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white bg-amber-600 rounded-full animate-pulse">
                {pendingHitlCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("customer")}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "customer"
                ? "bg-violet-600/20 text-violet-300 border border-violet-500/30"
                : "text-slate-300 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <LifeBuoy className="w-4 h-4" />
            <span>Customer Chat Portal</span>
          </button>
        </nav>

        {/* User Badge: Shriman Narayan (Admin) */}
        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5">
            <div className="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div className="text-left">
              <div className="text-xs font-semibold text-white">Shriman Narayan</div>
              <div className="text-[10px] text-emerald-400 font-mono">Platform Admin</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
