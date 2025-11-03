import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Pro - Document Q&A",
  description: "Modern RAG-powered document question answering",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
