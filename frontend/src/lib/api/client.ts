/**
 * API Client - FastAPI 백엔드 통신용 클라이언트
 * 인증, 에러 처리, 타입 안전성을 제공하는 HTTP 클라이언트
 */

import {
  ApiResponse,
  ApiClientConfig
} from '@/types';

export class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;
  private timeout: number;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout || 30000;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...config.defaultHeaders
    };
  }

  /**
   * HTTP 요청 실행
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // 자동으로 토큰 추가
    const headers: Record<string, string> = {};
    
    // Copy default headers
    Object.assign(headers, this.defaultHeaders);
    
    // Copy request headers if they exist
    if (options.headers) {
      Object.assign(headers, options.headers);
    }
    
    // Add authorization token
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    const config: RequestInit = {
      ...options,
      headers,
      signal: AbortSignal.timeout(this.timeout)
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        await this.handleHttpError(response);
      }

      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        const data = await response.json() as ApiResponse<T>;
        
        if ('success' in data && !data.success) {
          throw new ApiError(
            data.error.code,
            data.error.message,
            response.status,
            data.error.details
          );
        }
        
        return 'data' in data ? data.data : data as T;
      }
      
      return response.text() as unknown as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      if (error instanceof DOMException && error.name === 'TimeoutError') {
        throw new ApiError(
          'TIMEOUT',
          'Request timeout',
          408,
          { endpoint, timeout: this.timeout }
        );
      }
      
      throw new ApiError(
        'NETWORK_ERROR',
        'Network error occurred',
        0,
        { originalError: error, endpoint }
      );
    }
  }

  /**
   * HTTP 에러 처리
   */
  private async handleHttpError(response: Response): Promise<never> {
    let errorData: unknown;
    
    try {
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        errorData = await response.json();
      } else {
        errorData = await response.text();
      }
    } catch {
      errorData = null;
    }

    const isApiErrorResponse = (data: unknown): data is { error: { code: string; message: string; details?: unknown } } => {
      return data !== null && 
             typeof data === 'object' && 
             'error' in data && 
             typeof (data as Record<string, unknown>).error === 'object';
    };

    if (isApiErrorResponse(errorData)) {
      throw new ApiError(
        errorData.error.code,
        errorData.error.message,
        response.status,
        errorData.error.details
      );
    }

    // 표준 HTTP 에러 메시지
    const statusMessages: Record<number, string> = {
      400: 'Bad Request',
      401: 'Unauthorized',
      403: 'Forbidden',
      404: 'Not Found',
      422: 'Validation Error',
      500: 'Internal Server Error',
      502: 'Bad Gateway',
      503: 'Service Unavailable'
    };

    throw new ApiError(
      `HTTP_${response.status}`,
      statusMessages[response.status] || 'Unknown Error',
      response.status,
      errorData
    );
  }

  /**
   * 인증 토큰 설정
   */
  setAuthToken(token: string): void {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  /**
   * 인증 토큰 제거
   */
  removeAuthToken(): void {
    delete this.defaultHeaders['Authorization'];
  }

  /**
   * HTTP Methods
   */
  async get<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
    const url = params ? `${endpoint}?${new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key] = String(value);
        }
        return acc;
      }, {} as Record<string, string>)
    )}` : endpoint;
    
    return this.request<T>(url, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  /**
   * 파일 업로드 (multipart/form-data)
   */
  async upload<T>(endpoint: string, formData: FormData): Promise<T> {
    const headers = { ...this.defaultHeaders };
    delete headers['Content-Type']; // FormData가 자동으로 설정

    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers
    });
  }
}

/**
 * API 에러 클래스
 */
export class ApiError extends Error {
  constructor(
    public code: string,
    public message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }

  /**
   * 특정 에러 코드 확인
   */
  is(code: string): boolean {
    return this.code === code;
  }

  /**
   * 인증 에러 확인
   */
  isAuthError(): boolean {
    return this.status === 401 || this.code === 'UNAUTHORIZED';
  }

  /**
   * 유효성 검사 에러 확인
   */
  isValidationError(): boolean {
    return this.status === 422 || this.code === 'VALIDATION_ERROR';
  }

  /**
   * 네트워크 에러 확인
   */
  isNetworkError(): boolean {
    return this.code === 'NETWORK_ERROR' || this.code === 'TIMEOUT';
  }

  /**
   * JSON 직렬화
   */
  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      status: this.status,
      details: this.details
    };
  }
}

/**
 * 기본 API 클라이언트 인스턴스 생성
 */
export const createApiClient = (config?: Partial<ApiClientConfig>): ApiClient => {
  const defaultConfig: ApiClientConfig = {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    defaultHeaders: {
      'Accept': 'application/json',
    }
  };

  // 개발 환경에서만 베이스 URL 로그
  if (process.env.NODE_ENV === 'development') {
    console.log('🌐 API Client Base URL:', defaultConfig.baseUrl);
  }

  return new ApiClient({ ...defaultConfig, ...config });
};

// 기본 인스턴스 export
export const apiClient = createApiClient();
export default apiClient;