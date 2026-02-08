import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ClientWrapper } from "@/components/providers/client-wrapper";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  preload: false, // Disable preloading to avoid network requests during build
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  preload: false, // Disable preloading to avoid network requests during build
});

export const metadata: Metadata = {
  title: {
    default: 'TaskFlow - Transform Your Productivity',
    template: '%s | TaskFlow',
  },
  description: 'A futuristic, full-featured todo application with advanced UI/UX',
  keywords: ['task management', 'productivity', 'todo app', 'workflow', 'team collaboration'],
  authors: [{ name: 'TaskFlow Team' }],
  creator: 'TaskFlow Team',
  publisher: 'TaskFlow',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    title: 'TaskFlow - Transform Your Productivity',
    description: 'A futuristic, full-featured todo application with advanced UI/UX',
    url: 'https://www.taskflow.app',
    siteName: 'TaskFlow',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: '/og-image.svg',
        width: 1200,
        height: 630,
        alt: 'TaskFlow - Transform Your Productivity',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TaskFlow - Transform Your Productivity',
    description: 'A futuristic, full-featured todo application with advanced UI/UX',
    images: ['/og-image.svg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: 'https://www.taskflow.app',
  },
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
        <ClientWrapper>
          {children}
        </ClientWrapper>
      </body>
    </html>
  );
}
