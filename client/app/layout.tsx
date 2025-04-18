import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { PageWrapper } from "@/components/page-wrapper";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <PageWrapper>{children}</PageWrapper>
        <footer className="fixed bottom-0 bg-[#949494]/40 w-full h-24 text-[#0C0C0D]">
          <div className="flex flex-col gap-1 ml-24 h-full justify-center">
            <p className="text-md font-bold">
              Projekt na inzynierie oprogramowania
            </p>
            <a
              href="https://github.com/LeoTheOriginal/SoftEngProject"
              className="text-sm underline"
              target="_blank"
              rel="noreferrer"
            >
              Repozytorium na GitHub
            </a>
          </div>
        </footer>
      </body>
    </html>
  );
}
