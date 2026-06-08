import type { ButtonHTMLAttributes } from "react";

type Variant = "solid" | "outline";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const base =
  "inline-flex cursor-pointer items-center justify-center rounded-md px-4 py-2 text-sm font-medium " +
  "transition-colors focus-visible:outline-none focus-visible:ring-2 " +
  "focus-visible:ring-foreground focus-visible:ring-offset-2 " +
  "focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50";

const variants: Record<Variant, string> = {
  solid: "bg-foreground text-background hover:opacity-90",
  outline: "border border-border text-foreground hover:bg-foreground/5",
};

export default function Button({
  variant = "solid",
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${base} ${variants[variant]} ${className}`}
      {...props}
    />
  );
}
