import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'LWA — AI Clip Generator',
  description:
    'Turn any video into viral short-form clips. AI-generated hooks, captions, and timestamps for TikTok, Instagram Reels, YouTube Shorts, and more.',
  keywords: ['clip generator', 'AI video', 'short-form content', 'TikTok', 'Instagram Reels', 'YouTube Shorts'],
  authors: [{ name: 'LWA' }],
  robots: 'index, follow',
  openGraph: {
    title: 'LWA — AI Clip Generator',
    description: 'Turn any video into viral short-form clips in seconds.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LWA — AI Clip Generator',
    description: 'Turn any video into viral short-form clips in seconds.',
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#fff7fc' },
    { media: '(prefers-color-scheme: dark)', color: '#140f1d' },
  ],
  colorScheme: 'light dark',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="bg-mesh font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
