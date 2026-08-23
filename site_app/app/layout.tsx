import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI: From Rules to Real-World Agents",
  description: "A student-facing AI course with an interactive presentation and four practical labs.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
