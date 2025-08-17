import AuthInitializer from '@/components/auth/AuthInitializer';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Portfolio Manager',
  description: 'AI 시대의 프로젝트 관리 대중화',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <AuthInitializer />
        {children}
      </body>
    </html>
  );
}
