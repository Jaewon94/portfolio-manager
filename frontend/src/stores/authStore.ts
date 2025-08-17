import { authAPI, tokenUtils } from '@/lib/api/auth';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  username?: string;
  avatar_url?: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  validateToken: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      setLoading: (loading: boolean) => set({ isLoading: loading }),

      // 토큰 유효성 검증 함수
      validateToken: async () => {
        console.log('🔍 validateToken 시작');
        const token = tokenUtils.getAccessToken();
        console.log('🔍 토큰 확인:', token ? '있음' : '없음');

        if (!token) {
          console.log('🔍 토큰 없음 - 로그아웃 상태로 설정');
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
          return false;
        }

        try {
          console.log('🔍 /auth/me API 호출');
          const response = await fetch('http://localhost:8000/api/v1/auth/me', {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          console.log('🔍 API 응답 상태:', response.status);
          if (response.ok) {
            const user = await response.json();
            console.log('🔍 사용자 정보:', user);

            const userInfo: User = {
              id: user.id.toString(),
              name: user.name,
              email: user.email,
              username: user.github_username || user.email.split('@')[0],
              avatar_url: user.avatar_url,
            };

            console.log('🔍 상태 설정:', { userInfo, isAuthenticated: true });
            set({
              user: userInfo,
              isAuthenticated: true,
              isLoading: false,
            });
            return true;
          } else {
            console.log('🔍 토큰 무효 - 로그아웃 처리');
            // 토큰이 유효하지 않으면 제거
            tokenUtils.removeTokens();
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
            });
            return false;
          }
        } catch (error) {
          console.error('🔍 토큰 검증 실패:', error);
          tokenUtils.removeTokens();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
          return false;
        }
      },

      login: async (email: string, password: string): Promise<boolean> => {
        set({ isLoading: true });

        try {
          // 직접 API 호출로 테스트
          const response = await fetch(
            'http://localhost:8000/api/v1/auth/login',
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ email, password }),
            }
          );

          if (response.ok) {
            const data = await response.json();
            const { access_token, refresh_token, user } = data;

            // 토큰 저장
            tokenUtils.setTokens(access_token, refresh_token);

            // 사용자 정보 저장
            const userInfo: User = {
              id: user.id.toString(),
              name: user.name,
              email: user.email,
              username: user.github_username || user.email.split('@')[0],
            };

            set({
              user: userInfo,
              isAuthenticated: true,
              isLoading: false,
            });

            return true;
          } else {
            console.error('로그인 실패:', response.status, response.statusText);
            set({ isLoading: false });
            return false;
          }
        } catch (error) {
          console.error('로그인 실패:', error);
          set({ isLoading: false });
          return false;
        }
      },

      register: async (
        name: string,
        email: string,
        password: string
      ): Promise<boolean> => {
        set({ isLoading: true });

        try {
          // 실제 회원가입 API 호출
          const response = await fetch(
            'http://localhost:8000/api/v1/auth/register',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name, email, password }),
            }
          );

          if (response.ok) {
            // 회원가입 성공 시 로그인 상태로 설정하지 않음
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
            });
            return true;
          } else {
            const errorData = await response.json();
            console.error('회원가입 실패:', errorData);
            set({ isLoading: false });
            return false;
          }
        } catch (error) {
          console.error('회원가입 실패:', error);
          set({ isLoading: false });
          return false;
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          console.error('로그아웃 API 호출 실패:', error);
        } finally {
          // 토큰 제거
          tokenUtils.removeTokens();

          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },
    }),
    {
      name: 'auth-storage', // 로컬 스토리지 키 이름
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }), // 로컬 스토리지에 저장할 상태만 선택
      // 초기 상태를 로그아웃 상태로 설정
      onRehydrateStorage: () => (state) => {
        if (state) {
          // 토큰이 없으면 로그아웃 상태로 설정
          const accessToken = tokenUtils.getAccessToken();
          if (!accessToken) {
            state.user = null;
            state.isAuthenticated = false;
          }
        }
      },
    }
  )
);
