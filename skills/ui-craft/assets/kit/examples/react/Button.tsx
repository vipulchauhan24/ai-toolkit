// A ported kit component. It keeps the kit's class names, so component.css still styles it.
import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";

type Style = { variant?: "primary" | "secondary" | "ghost" | "danger"; size?: "sm" | "md" | "lg"; children: ReactNode };

const classes = ({ variant = "primary", size = "md" }: Style) =>
  ["btn", `btn--${variant}`, size !== "md" && `btn--${size}`].filter(Boolean).join(" ");

export function Button(props: Style & ButtonHTMLAttributes<HTMLButtonElement>) {
  const { variant, size, children, ...rest } = props;
  return <button className={classes({ variant, size, children })} {...rest}>{children}</button>;
}

export function ButtonLink(props: Style & AnchorHTMLAttributes<HTMLAnchorElement>) {
  const { variant, size, children, ...rest } = props;
  return <a className={classes({ variant, size, children })} {...rest}>{children}</a>;
}
