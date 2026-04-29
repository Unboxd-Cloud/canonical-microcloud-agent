import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Canonical MicroCloud Agent UI",
  description: "Next.js chat template for the Canonical MicroCloud agent"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
