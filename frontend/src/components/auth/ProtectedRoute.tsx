'use client';

import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  console.log('🔒 ProtectedRoute - 상태:', { isAuthenticated, isLoading });

  useEffect(() => {
    console.log('🔒 ProtectedRoute useEffect:', { isAuthenticated, isLoading });
    if (!isLoading && !isAuthenticated) {
      console.log('🔒 로그인 페이지로 리다이렉트');
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // 항상 같은 구조를 유지하여 Fast Refresh 오류 방지
  return (
    <div className="min-h-screen">
      {isLoading ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-4 text-gray-600">로딩 중...</p>
          </div>
        </div>
      ) : isAuthenticated ? (
        <>{children}</>
      ) : (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-4 text-gray-600">인증 확인 중...</p>
          </div>
        </div>
      )}
    </div>
  );
}
