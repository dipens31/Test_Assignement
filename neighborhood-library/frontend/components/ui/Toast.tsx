"use client";

import { useEffect, useState, createContext, useContext, useCallback } from "react";
import type { ReactNode } from "react";
import { CheckCircle, XCircle, AlertCircle, X, Info } from "lucide-react";
import clsx from "clsx";

type ToastVariant = "success" | "error" | "warning" | "info";

interface Toast {
  id: string;
  variant: ToastVariant;
  message: string;
}

interface ToastContextValue {
  toast: (variant: ToastVariant, message: string) => void;
}

const ToastContext = createContext<ToastContextValue>({ toast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

const ICONS: Record<ToastVariant, ReactNode> = {
  success: <CheckCircle className="w-4 h-4" />,
  error:   <XCircle    className="w-4 h-4" />,
  warning: <AlertCircle className="w-4 h-4" />,
  info:    <Info        className="w-4 h-4" />,
};

const STYLES: Record<ToastVariant, string> = {
  success: "bg-emerald-50 border-emerald-200 text-emerald-800",
  error:   "bg-red-50     border-red-200     text-red-800",
  warning: "bg-amber-50   border-amber-200   text-amber-800",
  info:    "bg-brand-50   border-brand-200   text-brand-800",
};

const ICON_STYLES: Record<ToastVariant, string> = {
  success: "text-emerald-500",
  error:   "text-red-500",
  warning: "text-amber-500",
  info:    "text-brand-500",
};

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const show = requestAnimationFrame(() => setVisible(true));
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => onDismiss(toast.id), 300);
    }, 4000);
    return () => { cancelAnimationFrame(show); clearTimeout(timer); };
  }, [toast.id, onDismiss]);

  return (
    <div
      className={clsx(
        "flex items-start gap-3 rounded-xl border px-4 py-3 shadow-lg transition-all duration-300 min-w-[280px] max-w-sm",
        STYLES[toast.variant],
        visible ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2",
      )}
    >
      <span className={clsx("mt-0.5 flex-shrink-0", ICON_STYLES[toast.variant])}>
        {ICONS[toast.variant]}
      </span>
      <p className="flex-1 text-sm font-medium leading-5">{toast.message}</p>
      <button
        onClick={() => { setVisible(false); setTimeout(() => onDismiss(toast.id), 300); }}
        className="flex-shrink-0 rounded p-0.5 opacity-60 hover:opacity-100 transition-opacity"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((variant: ToastVariant, message: string) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, variant, message }]);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed top-5 right-5 z-50 flex flex-col gap-2 items-end">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
