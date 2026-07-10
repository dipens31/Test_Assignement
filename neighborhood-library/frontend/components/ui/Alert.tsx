import clsx from "clsx";
import { CheckCircle, XCircle, AlertTriangle, Info, X } from "lucide-react";

type Variant = "success" | "error" | "warning" | "info";

const styles: Record<Variant, string> = {
  success: "bg-emerald-50 border-emerald-200 text-emerald-800",
  error:   "bg-red-50     border-red-200     text-red-800",
  warning: "bg-amber-50   border-amber-200   text-amber-800",
  info:    "bg-brand-50   border-brand-200   text-brand-800",
};

const iconStyles: Record<Variant, string> = {
  success: "text-emerald-500",
  error:   "text-red-500",
  warning: "text-amber-500",
  info:    "text-brand-500",
};

const IconMap = {
  success: CheckCircle,
  error:   XCircle,
  warning: AlertTriangle,
  info:    Info,
};

interface AlertProps {
  variant?: Variant;
  title?: string;
  message: string;
  onClose?: () => void;
}

export default function Alert({ variant = "info", title, message, onClose }: AlertProps) {
  const Icon = IconMap[variant];
  return (
    <div className={clsx("flex items-start gap-3 rounded-xl border px-4 py-3 text-sm", styles[variant])} role="alert">
      <Icon className={clsx("w-4 h-4 flex-shrink-0 mt-0.5", iconStyles[variant])} />
      <div className="flex-1 min-w-0">
        {title && <p className="font-semibold mb-0.5">{title}</p>}
        <p className="leading-snug">{message}</p>
      </div>
      {onClose && (
        <button onClick={onClose} className="flex-shrink-0 rounded p-0.5 opacity-60 hover:opacity-100 transition-opacity" aria-label="Close">
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
