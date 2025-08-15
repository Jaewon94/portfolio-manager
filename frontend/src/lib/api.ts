import axios, { AxiosResponse } from 'axios'
import { User, Project, Note, Media, SearchResult } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// API 클라이언트 인스턴스 생성
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 응답 타입 정의
export interface ApiResponse<T = Record<string, unknown>> {
  success: boolean
  data: T
  message?: string
  meta?: {
    total?: number
    page?: number
    pageSize?: number
    totalPages?: number
  }
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
  timestamp: string
  path: string
}

// 요청 인터셉터 - 인증 토큰 추가
apiClient.interceptors.request.use(
  (config) => {
    // 세션 스토리지나 쿠키에서 토큰 가져오기
    const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터 - 에러 처리
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // 인증 실패 시 로그인 페이지로 리다이렉트
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin'
      }
    }
    return Promise.reject(error)
  }
)

// API 함수들
export const api = {
  // 인증 관련
  auth: {
    me: () => apiClient.get<ApiResponse<User>>('/auth/me'),
    logout: () => apiClient.post<ApiResponse<void>>('/auth/logout'),
    refresh: () => apiClient.post<ApiResponse<{ token: string; expires_at: string }>>('/auth/refresh'),
  },

  // 프로젝트 관련
  projects: {
    list: (params?: Record<string, unknown>) => apiClient.get<ApiResponse<Project[]>>('/projects', { params }),
    get: (id: string) => apiClient.get<ApiResponse<Project>>(`/projects/${id}`),
    create: (data: Partial<Project>) => apiClient.post<ApiResponse<Project>>('/projects', data),
    update: (id: string, data: Partial<Project>) => apiClient.patch<ApiResponse<Project>>(`/projects/${id}`, data),
    delete: (id: string) => apiClient.delete<ApiResponse<void>>(`/projects/${id}`),
    updateStatus: (id: string, status: string) => 
      apiClient.patch<ApiResponse<Project>>(`/projects/${id}/status`, { status }),
    incrementViews: (id: string) => apiClient.post<ApiResponse<{ view_count: number }>>(`/projects/${id}/views`),
  },

  // 노트 관련
  notes: {
    list: (projectId: string, params?: Record<string, unknown>) => 
      apiClient.get<ApiResponse<Note[]>>(`/projects/${projectId}/notes`, { params }),
    get: (id: string) => apiClient.get<ApiResponse<Note>>(`/notes/${id}`),
    create: (projectId: string, data: Partial<Note>) => 
      apiClient.post<ApiResponse<Note>>(`/projects/${projectId}/notes`, data),
    update: (id: string, data: Partial<Note>) => apiClient.patch<ApiResponse<Note>>(`/notes/${id}`, data),
    delete: (id: string) => apiClient.delete<ApiResponse<void>>(`/notes/${id}`),
    pin: (id: string, isPinned: boolean) => 
      apiClient.patch<ApiResponse<Note>>(`/notes/${id}/pin`, { is_pinned: isPinned }),
    archive: (id: string, isArchived: boolean) => 
      apiClient.patch<ApiResponse<Note>>(`/notes/${id}/archive`, { is_archived: isArchived }),
  },

  // 미디어 관련
  media: {
    upload: (formData: FormData) => 
      apiClient.post<ApiResponse<Media>>('/media/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      }),
    list: (params?: Record<string, unknown>) => apiClient.get<ApiResponse<Media[]>>('/media', { params }),
    update: (id: string, data: Partial<Media>) => apiClient.patch<ApiResponse<Media>>(`/media/${id}`, data),
    delete: (id: string) => apiClient.delete<ApiResponse<void>>(`/media/${id}`),
  },

  // 검색 관련
  search: {
    global: (params: Record<string, unknown>) => apiClient.get<ApiResponse<SearchResult>>('/search', { params }),
    autocomplete: (params: Record<string, unknown>) => apiClient.get<ApiResponse<string[]>>('/search/autocomplete', { params }),
    trending: (params?: Record<string, unknown>) => apiClient.get<ApiResponse<string[]>>('/search/trending', { params }),
  },

  // GitHub 저장소 관련
  github: {
    connect: (projectId: string, githubUrl: string) => 
      apiClient.post<ApiResponse<Project>>(`/projects/${projectId}/github`, { github_url: githubUrl }),
    sync: (githubRepoId: string) => 
      apiClient.post<ApiResponse<Record<string, unknown>>>(`/github/${githubRepoId}/sync`),
    disconnect: (githubRepoId: string) => 
      apiClient.delete<ApiResponse<void>>(`/github/${githubRepoId}`),
  },

  // 시스템 헬스체크
  health: () => apiClient.get<ApiResponse<{ status: string; timestamp: string }>>('/health'),
  info: () => apiClient.get<ApiResponse<{ version: string; environment: string }>>('/info'),
}