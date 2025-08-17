/**
 * API Client - 통합 API 서비스
 * 모든 API 서비스를 하나의 인스턴스로 통합 제공
 */

import { createApiClient, ApiClient, ApiError } from './client';
import { AuthService } from './services/auth';
import { ProjectsService } from './services/projects';
import { NotesService } from './services/notes';
import { MediaService } from './services/media';
import { SearchService } from './services/search';
import { ApiClientConfig } from '@/types';

/**
 * 통합 API 서비스 클래스
 */
export class ApiService {
  private client: ApiClient;
  
  public readonly auth: AuthService;
  public readonly projects: ProjectsService;
  public readonly notes: NotesService;
  public readonly media: MediaService;
  public readonly search: SearchService;

  constructor(config?: Partial<ApiClientConfig>) {
    this.client = createApiClient(config);
    
    // 서비스 인스턴스 생성
    this.auth = new AuthService(this.client);
    this.projects = new ProjectsService(this.client);
    this.notes = new NotesService(this.client);
    this.media = new MediaService(this.client);
    this.search = new SearchService(this.client);
  }

  /**
   * 인증 토큰 설정 (모든 서비스에 적용)
   */
  setAuthToken(token: string): void {
    this.client.setAuthToken(token);
  }

  /**
   * 인증 토큰 제거 (모든 서비스에서 제거)
   */
  removeAuthToken(): void {
    this.client.removeAuthToken();
  }

  /**
   * API 클라이언트 인스턴스 반환
   */
  getClient(): ApiClient {
    return this.client;
  }

  /**
   * 헬스 체크
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    timestamp: string;
    services: Record<string, string>;
    version: string;
  }> {
    try {
      return await this.client.get('/api/health');
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'HEALTH_CHECK_FAILED',
        'Health check failed',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * API 서버 정보 조회
   */
  async getServerInfo(): Promise<{
    version: string;
    environment: string;
    uptime: number;
    features: string[];
  }> {
    try {
      return await this.client.get('/api/info');
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_SERVER_INFO_FAILED',
        'Failed to get server info',
        500,
        { originalError: error }
      );
    }
  }
}

/**
 * 기본 API 서비스 인스턴스 생성
 */
export const createApiService = (config?: Partial<ApiClientConfig>): ApiService => {
  return new ApiService(config);
};

/**
 * 싱글톤 API 서비스 인스턴스
 */
export const api = createApiService();

// 개별 서비스들도 export (필요시 직접 사용)
export { AuthService } from './services/auth';
export { ProjectsService } from './services/projects';
export { NotesService } from './services/notes';
export { MediaService } from './services/media';
export { SearchService } from './services/search';

// 클라이언트와 에러 클래스도 export
export { ApiClient, createApiClient, ApiError } from './client';

// 기본 export는 API 서비스 인스턴스
export default api;