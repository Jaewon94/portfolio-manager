/**
 * Auth Service - 인증 관련 API 호출
 */

import { ApiClient, ApiError } from '../client';
import {
  LoginRequest,
  LoginResponse,
  LogoutRequest,
  RefreshTokenRequest,
  RefreshTokenResponse,
  MeResponse
} from '@/types';

export class AuthService {
  constructor(private client: ApiClient) {}

  /**
   * 소셜 로그인 (GitHub/Google)
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      return await this.client.post<LoginResponse>('/auth/login/', data);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'LOGIN_FAILED',
        'Login failed',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 로그아웃
   */
  async logout(data?: LogoutRequest): Promise<{ success: boolean }> {
    try {
      const response = await this.client.post<{ success: boolean }>('/auth/logout/', data);
      // 로그아웃 성공 시 클라이언트에서 토큰 제거
      this.client.removeAuthToken();
      return response;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'LOGOUT_FAILED',
        'Logout failed',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 토큰 갱신
   */
  async refreshToken(data: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    try {
      const response = await this.client.post<RefreshTokenResponse>('/auth/refresh/', data);
      // 새 토큰으로 업데이트
      this.client.setAuthToken(response.session_token);
      return response;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'TOKEN_REFRESH_FAILED',
        'Token refresh failed',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 현재 사용자 정보 조회
   */
  async me(): Promise<MeResponse> {
    try {
      return await this.client.get<MeResponse>('/auth/me/');
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_USER_FAILED',
        'Failed to get user info',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 인증 토큰 설정
   */
  setAuthToken(token: string): void {
    this.client.setAuthToken(token);
  }

  /**
   * 인증 토큰 제거
   */
  removeAuthToken(): void {
    this.client.removeAuthToken();
  }
}