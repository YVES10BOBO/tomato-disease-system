import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tomato Disease Detection System",
  description: "AI & IoT-Based System for Early Detection and Prevention of Tomato Diseases",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-gray-50">{children}</body>
    </html>
  );
}
