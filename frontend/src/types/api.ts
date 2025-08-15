/**
 * Portfolio Manager API Types
 * API 엔드포인트별 요청/응답 타입 정의
 */

import {
  User,
  Project,
  Note,
  Media,
  GithubRepository,
  ProjectWithRelations,
  NoteWithRelations,
  UserWithRelations,
  CreateProjectDto,
  UpdateProjectDto,
  CreateNoteDto,
  UpdateNoteDto,
  CreateMediaDto,
  ProjectFilters,
  NoteFilters,
  SearchParams,
  ApiResponse
} from './database';

// =============================================================================
// Authentication API Types
// =============================================================================

export interface LoginRequest {
  provider: 'github' | 'google';
  redirect_url?: string;
}

export interface LoginResponse {
  user: User;
  session_token: string;
  expires: string;
  redirect_url?: string;
}

export interface LogoutRequest {
  session_token?: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  session_token: string;
  expires: string;
}

export interface MeResponse {
  user: UserWithRelations;
  session: {
    expires: string;
    ip_address?: string;
    user_agent?: string;
  };
}

// =============================================================================
// Projects API Types
// =============================================================================

export type GetProjectsRequest = ProjectFilters;

export interface GetProjectsResponse {
  projects: ProjectWithRelations[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
}

export interface GetProjectRequest {
  id: string;
  include_notes?: boolean;
  include_media?: boolean;
  include_github?: boolean;
}

export interface GetProjectResponse {
  project: ProjectWithRelations;
}

export type CreateProjectRequest = CreateProjectDto;

export interface CreateProjectResponse {
  project: Project;
}

export interface UpdateProjectRequest extends UpdateProjectDto {
  id: string;
}

export interface UpdateProjectResponse {
  project: Project;
}

export interface DeleteProjectRequest {
  id: string;
}

export interface DeleteProjectResponse {
  deleted: boolean;
  id: string;
}

// =============================================================================
// Notes API Types
// =============================================================================

export interface GetNotesRequest extends NoteFilters {
  project_id: string;
}

export interface GetNotesResponse {
  notes: NoteWithRelations[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
}

export interface GetNoteRequest {
  id: string;
  include_media?: boolean;
  include_project?: boolean;
}

export interface GetNoteResponse {
  note: NoteWithRelations;
}

export interface CreateNoteRequest extends CreateNoteDto {
  project_id: string;
}

export interface CreateNoteResponse {
  note: Note;
}

export interface UpdateNoteRequest extends UpdateNoteDto {
  id: string;
}

export interface UpdateNoteResponse {
  note: Note;
}

export interface DeleteNoteRequest {
  id: string;
}

export interface DeleteNoteResponse {
  deleted: boolean;
  id: string;
}

// =============================================================================
// Media API Types
// =============================================================================

export interface UploadMediaRequest extends CreateMediaDto {
  file: File;
}

export interface UploadMediaResponse {
  media: Media;
  upload_url?: string; // 업로드된 파일 URL
}

export interface GetMediaRequest {
  id: string;
}

export interface GetMediaResponse {
  media: Media;
  download_url: string;
}

export interface DeleteMediaRequest {
  id: string;
}

export interface DeleteMediaResponse {
  deleted: boolean;
  id: string;
}

// =============================================================================
// Search API Types
// =============================================================================

export type SearchRequest = SearchParams;

export interface SearchResponse {
  results: {
    projects?: ProjectWithRelations[];
    notes?: NoteWithRelations[];
    users?: User[];
  };
  total: number;
  query: string;
  took_ms: number;
}

// Legacy SearchResult type for backward compatibility
export interface SearchResult {
  projects?: Array<ProjectWithRelations & {
    highlight?: {
      title?: string;
      description?: string;
    };
    type: 'project';
  }>;
  notes?: Array<NoteWithRelations & {
    highlight?: {
      title?: string;
      content?: string;
    };
    type: 'note';
    note_type: string;
  }>;
  users?: Array<User & {
    highlight?: {
      name?: string;
      bio?: string;
    };
    type: 'user';
    project_count?: number;
  }>;
}

export interface AutocompleteRequest {
  query: string;
  type?: 'projects' | 'notes' | 'tags' | 'tech_stack';
  limit?: number;
}

export interface AutocompleteResponse {
  suggestions: {
    type: string;
    text: string;
    count?: number;
  }[];
}

// =============================================================================
// GitHub Integration API Types
// =============================================================================

export interface SyncGithubRepositoryRequest {
  project_id: string;
  github_url: string;
  auto_sync?: boolean;
}

export interface SyncGithubRepositoryResponse {
  github_repository: GithubRepository;
  synced_at: string;
}

export interface GetGithubRepositoryRequest {
  project_id: string;
}

export interface GetGithubRepositoryResponse {
  github_repository: GithubRepository;
  sync_status: 'active' | 'inactive' | 'error';
  last_sync?: string;
  next_sync?: string;
}

// =============================================================================
// Analytics API Types
// =============================================================================

export interface GetAnalyticsRequest {
  project_id?: string;
  date_from?: string;
  date_to?: string;
  metrics?: ('views' | 'likes' | 'shares' | 'downloads')[];
}

export interface GetAnalyticsResponse {
  metrics: {
    views: number;
    likes: number;
    shares: number;
    downloads: number;
  };
  chart_data: {
    date: string;
    views: number;
    likes: number;
  }[];
  top_projects: {
    project: Project;
    views: number;
    likes: number;
  }[];
}

// =============================================================================
// Utility API Types
// =============================================================================

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    database: 'connected' | 'disconnected';
    redis?: 'connected' | 'disconnected';
    storage: 'available' | 'unavailable';
  };
  version: string;
}

export interface GetTagsResponse {
  tags: {
    name: string;
    count: number;
    type: 'project' | 'note';
  }[];
}

export interface GetTechStackResponse {
  tech_stack: {
    name: string;
    count: number;
    category?: string;
  }[];
}

export interface GetCategoriesResponse {
  categories: {
    name: string;
    count: number;
    description?: string;
  }[];
}

// =============================================================================
// Wrapped API Response Types
// =============================================================================

// Authentication
export type LoginApiResponse = ApiResponse<LoginResponse>;
export type LogoutApiResponse = ApiResponse<{ success: boolean }>;
export type RefreshTokenApiResponse = ApiResponse<RefreshTokenResponse>;
export type MeApiResponse = ApiResponse<MeResponse>;

// Projects
export type GetProjectsApiResponse = ApiResponse<GetProjectsResponse>;
export type GetProjectApiResponse = ApiResponse<GetProjectResponse>;
export type CreateProjectApiResponse = ApiResponse<CreateProjectResponse>;
export type UpdateProjectApiResponse = ApiResponse<UpdateProjectResponse>;
export type DeleteProjectApiResponse = ApiResponse<DeleteProjectResponse>;

// Notes
export type GetNotesApiResponse = ApiResponse<GetNotesResponse>;
export type GetNoteApiResponse = ApiResponse<GetNoteResponse>;
export type CreateNoteApiResponse = ApiResponse<CreateNoteResponse>;
export type UpdateNoteApiResponse = ApiResponse<UpdateNoteResponse>;
export type DeleteNoteApiResponse = ApiResponse<DeleteNoteResponse>;

// Media
export type UploadMediaApiResponse = ApiResponse<UploadMediaResponse>;
export type GetMediaApiResponse = ApiResponse<GetMediaResponse>;
export type DeleteMediaApiResponse = ApiResponse<DeleteMediaResponse>;

// Search
export type SearchApiResponse = ApiResponse<SearchResponse>;
export type AutocompleteApiResponse = ApiResponse<AutocompleteResponse>;

// GitHub Integration
export type SyncGithubRepositoryApiResponse = ApiResponse<SyncGithubRepositoryResponse>;
export type GetGithubRepositoryApiResponse = ApiResponse<GetGithubRepositoryResponse>;

// Analytics
export type GetAnalyticsApiResponse = ApiResponse<GetAnalyticsResponse>;

// Utilities
export type HealthCheckApiResponse = ApiResponse<HealthCheckResponse>;
export type GetTagsApiResponse = ApiResponse<GetTagsResponse>;
export type GetTechStackApiResponse = ApiResponse<GetTechStackResponse>;
export type GetCategoriesApiResponse = ApiResponse<GetCategoriesResponse>;

// =============================================================================
// API Client Configuration Types
// =============================================================================

export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  defaultHeaders?: Record<string, string>;
  auth?: {
    type: 'bearer' | 'cookie';
    token?: string;
  };
  retry?: {
    attempts: number;
    delay: number;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
  status: number;
  timestamp: string;
  path: string;
}