import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Knowledge Assistant',
  description: 'Ask questions over your documents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="app-body">
        <div className="app-bg" aria-hidden="true" />
        <div className="app-container">{children}</div>
      </body>
    </html>
  );
}
