'use client';

import { useAuthStore } from '@/stores/authStore';
import { useEffect } from 'react';

export default function AuthInitializer() {
  const { isAuthenticated, validateToken } = useAuthStore();

  useEffect(() => {
    console.log('🔍 AuthInitializer - 현재 상태:', { isAuthenticated });

    // 토큰이 있으면 무조건 검증 (상태와 관계없이)
    const token = localStorage.getItem('access_token');
    if (token) {
      console.log('🔍 토큰 발견 - 검증 시작');
      validateToken();
    } else {
      console.log('🔍 토큰 없음 - 인증되지 않은 상태');
    }
  }, [validateToken, isAuthenticated]); // isAuthenticated 의존성 추가

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}
