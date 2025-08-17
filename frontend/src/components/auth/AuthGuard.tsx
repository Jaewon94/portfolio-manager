/**
 * 인증 가드 컴포넌트 - 로그인이 필요한 페이지 보호
 */

'use client';

import React, { ReactNode } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { LoginForm } from './LoginForm';
import { Loader2 } from 'lucide-react';

interface AuthGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
  requireAuth?: boolean;
}

export function AuthGuard({ 
  children, 
  fallback, 
  requireAuth = true 
}: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuthStore();

  // 로딩 중일 때
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto" />
          <p className="text-muted-foreground">로딩 중...</p>
        </div>
      </div>
    );
  }

  // 인증이 필요하지 않은 경우 바로 children 렌더링
  if (!requireAuth) {
    return <>{children}</>;
  }

  // 인증되지 않은 경우
  if (!isAuthenticated) {
    if (fallback) {
      return <>{fallback}</>;
    }

    // 기본 로그인 폼 표시
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-full max-w-md">
          <LoginForm />
        </div>
      </div>
    );
  }

  // 인증된 사용자는 children 렌더링
  return <>{children}</>;
}

/**
 * 공개 페이지 래퍼 (인증 불필요)
 */
export function PublicRoute({ children }: { children: ReactNode }) {
  return (
    <AuthGuard requireAuth={false}>
      {children}
    </AuthGuard>
  );
}

/**
 * 보호된 페이지 래퍼 (인증 필요)
 */
export function ProtectedRoute({ 
  children, 
  fallback 
}: { 
  children: ReactNode;
  fallback?: ReactNode;
}) {
  return (
    <AuthGuard requireAuth={true} fallback={fallback}>
      {children}
    </AuthGuard>
  );
}