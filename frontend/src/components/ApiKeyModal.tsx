"use client";

import React, { useEffect, useState } from "react";
import {
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
  XCircle,
} from "lucide-react";
import { testPersonalGeminiKey } from "@/lib/api";
import {
  clearPersonalGeminiConfig,
  GEMINI_MODEL_OPTIONS,
  loadPersonalGeminiConfig,
  savePersonalGeminiConfig,
} from "@/lib/geminiSettings";

interface ApiKeyModalProps {
  open: boolean;
  onClose: () => void;
  onSaved?: (hasKey: boolean, model: string) => void;
}

export function ApiKeyModal({ open, onClose, onSaved }: ApiKeyModalProps) {
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("gemini-3.5-flash-lite");
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [savedNotice, setSavedNotice] = useState(false);

  useEffect(() => {
    if (!open) return;
    const cfg = loadPersonalGeminiConfig();
    setApiKey(cfg.apiKey);
    setModel(cfg.model);
    setTestResult(null);
    setSavedNotice(false);
  }, [open]);

  if (!open) return null;

  const handleSave = () => {
    savePersonalGeminiConfig({ apiKey, model });
    setSavedNotice(true);
    onSaved?.(Boolean(apiKey.trim()), model);
    window.setTimeout(() => {
      onClose();
    }, 450);
  };

  const handleClear = () => {
    clearPersonalGeminiConfig();
    setApiKey("");
    setModel("gemini-3.5-flash-lite");
    setTestResult(null);
    onSaved?.(false, "gemini-3.5-flash-lite");
  };

  const handleTest = async () => {
    if (!apiKey.trim()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testPersonalGeminiKey(apiKey.trim(), model);
      setTestResult({ ok: res.ok, message: res.message });
    } catch (err: unknown) {
      setTestResult({
        ok: false,
        message: err instanceof Error ? err.message : "Connection test failed.",
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 p-4 backdrop-blur-[1px]">
      <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700">
              <KeyRound className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Personal Gemini API Key</h2>
              <p className="text-xs text-slate-500">
                Optional upgrade for higher-tier models & higher quotas
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close API key modal"
            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 px-6 py-5">
          <div className="rounded-xl border border-blue-100 bg-blue-50/70 p-3.5 text-xs leading-relaxed text-slate-700">
            <p className="font-semibold text-blue-900">
              Reading & Listening grading is 100% deterministic (0 API calls needed).
            </p>
            <p className="mt-1">
              Gemini powers optional AI distractor breakdowns, studio Listening TTS audio, and
              upcoming Writing & Speaking scoring. Add your own Paid/Tier-1+ Gemini key here to
              unlock faster quotas and higher-reasoning models without editing server files.
            </p>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-bold tracking-wide text-slate-700 uppercase">
              Your Gemini API Key (Google AI Studio)
            </label>
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <input
                  type={showKey ? "text" : "password"}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="AIzaSy…"
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 pr-9 font-mono text-sm text-slate-900 focus:border-indigo-600 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setShowKey((s) => !s)}
                  className="absolute top-1/2 right-2.5 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  aria-label={showKey ? "Hide API key" : "Show API key"}
                >
                  {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <button
                type="button"
                disabled={!apiKey.trim() || testing}
                onClick={handleTest}
                className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-50"
              >
                {testing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5 text-indigo-600" />}
                Test Key
              </button>
            </div>
            {testResult && (
              <p
                className={`mt-2 inline-flex items-center gap-1.5 text-xs font-medium ${
                  testResult.ok ? "text-emerald-700" : "text-rose-700"
                }`}
              >
                {testResult.ok ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 shrink-0" />
                )}
                {testResult.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-bold tracking-wide text-slate-700 uppercase">
              Preferred Model Tier
            </label>
            <div className="space-y-2">
              {GEMINI_MODEL_OPTIONS.map((opt) => (
                <label
                  key={opt.id}
                  className={`flex cursor-pointer items-start gap-2.5 rounded-xl border p-3 transition ${
                    model === opt.id
                      ? "border-indigo-600 bg-indigo-50/50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="gemini-model"
                    value={opt.id}
                    checked={model === opt.id}
                    onChange={() => setModel(opt.id)}
                    className="mt-1 accent-indigo-600"
                  />
                  <div className="flex-1 text-xs">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-slate-900">{opt.label}</span>
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                        {opt.tier}
                      </span>
                    </div>
                    <p className="mt-0.5 text-slate-600">{opt.note}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-[11px] text-slate-600">
            <ShieldCheck className="h-4 w-4 shrink-0 text-emerald-600" />
            Stored locally in your browser only (<code className="font-mono">localStorage</code>)
            and sent securely per request—never written to disk or Git.
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-slate-200 px-6 py-3.5">
          <button
            type="button"
            onClick={handleClear}
            className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear Key
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-200 px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-indigo-700"
            >
              {savedNotice ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Saved!
                </>
              ) : (
                "Save Settings"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
