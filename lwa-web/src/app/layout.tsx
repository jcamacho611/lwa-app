import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'LWA — AI Content Operating System',
  description:
    'Turn one long video into a ranked clip engine. AI-generated hooks, captions, timestamps, packaging angles, and workflow-ready short-form assets in one premium workspace.',
  keywords: ['clip generator', 'AI video', 'short-form content', 'TikTok', 'Instagram Reels', 'YouTube Shorts', 'content repurposing', 'AI content'],
  authors: [{ name: 'LWA' }],
  robots: 'index, follow',
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
  },
  openGraph: {
    title: 'LWA — AI Content Operating System',
    description: 'Turn one long video into a ranked clip engine.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LWA — AI Content Operating System',
    description: 'Turn one long video into a ranked clip engine.',
  },
};

export const viewport: Viewport = {
  themeColor: '#050816',
  colorScheme: 'dark',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} dark`} suppressHydrationWarning>
      <body className="bg-mesh font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
