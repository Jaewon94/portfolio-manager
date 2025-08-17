import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
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
        <div className="flex h-screen bg-background">
          {/* 사이드바 */}
          <Sidebar />

          {/* 메인 콘텐츠 영역 */}
          <div className="flex-1 flex flex-col">
            {/* 헤더 */}
            <Header />

            {/* 메인 콘텐츠 */}
            <main className="flex-1 overflow-auto">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
