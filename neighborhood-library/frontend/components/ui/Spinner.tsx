import clsx from "clsx";

const sizes = { sm: "h-4 w-4 border-[1.5px]", md: "h-5 w-5 border-2", lg: "h-8 w-8 border-2" };

export default function Spinner({ size = "md", className }: { size?: "sm" | "md" | "lg"; className?: string }) {
  return (
    <span
      className={clsx("inline-block rounded-full border-current border-t-transparent animate-spin text-brand-600", sizes[size], className)}
      role="status"
      aria-label="Loading"
    />
  );
}

export function PageSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-3 text-slate-400">
      <Spinner size="lg" />
      <span className="text-sm">Loading…</span>
    </div>
  );
}
