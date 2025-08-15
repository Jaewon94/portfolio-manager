/**
 * Portfolio Manager Database Types
 * ERD 설계에 기반한 7개 핵심 엔티티 타입 정의 (3NF 준수)
 */

// =============================================================================
// Enum Types
// =============================================================================

export enum UserRole {
  USER = 'user',
  ADMIN = 'admin'
}

export enum AuthProvider {
  GITHUB = 'github',
  GOOGLE = 'google'
}

export enum ProjectStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived'
}

export enum ProjectVisibility {
  PUBLIC = 'public',
  PRIVATE = 'private',
  UNLISTED = 'unlisted'
}

export enum NoteType {
  LEARN = 'learn',
  CHANGE = 'change',
  RESEARCH = 'research'
}

export enum MediaType {
  IMAGE = 'image',
  VIDEO = 'video',
  DOCUMENT = 'document'
}

export enum TargetType {
  PROJECT = 'project',
  NOTE = 'note'
}

// =============================================================================
// Core Entity Types (7개 핵심 엔티티)
// =============================================================================

/**
 * User - 전역 사용자
 */
export interface User {
  id: string; // UUID
  email: string; // Unique
  name: string;
  bio?: string;
  avatar_url?: string;
  github_username?: string;
  role: UserRole;
  is_verified: boolean;
  created_at: Date;
  updated_at: Date;
}

/**
 * AuthAccount - 소셜 로그인 연동 (GitHub/Google)
 */
export interface AuthAccount {
  id: string; // UUID
  user_id: string; // FK to User
  provider: AuthProvider;
  provider_account_id: string;
  access_token?: string;
  refresh_token?: string;
  expires_at?: Date;
  token_type?: string;
  scope?: string;
  id_token?: string;
  created_at: Date;
  updated_at: Date;
}

/**
 * Session - 세션/토큰 관리
 */
export interface Session {
  id: string; // UUID
  user_id: string; // FK to User
  session_token: string; // Unique
  expires: Date;
  ip_address?: string;
  user_agent?: string;
  created_at: Date;
  updated_at: Date;
}

/**
 * Project - 포트폴리오 프로젝트 메타데이터
 */
export interface Project {
  id: string; // UUID
  owner_id: string; // FK to User
  slug: string; // URL-friendly identifier
  title: string;
  description?: string;
  content: Record<string, unknown>; // JSONB - 유연한 콘텐츠 구조
  tech_stack: string[]; // Array - 기술 스택
  categories: string[]; // Array - 카테고리
  tags: string[]; // Array - 태그
  status: ProjectStatus;
  visibility: ProjectVisibility;
  featured: boolean;
  view_count: number;
  like_count: number;
  created_at: Date;
  updated_at: Date;
}

/**
 * GithubRepository - GitHub 저장소 정보 (1:1, 3NF 준수)
 */
export interface GithubRepository {
  id: string; // UUID
  project_id: string; // FK to Project (Unique - 1:1 관계)
  github_url: string;
  repository_name: string;
  stars: number;
  forks: number;
  language?: string;
  license?: string;
  last_commit_date?: Date;
  sync_enabled: boolean;
  created_at: Date;
  updated_at: Date;
}

/**
 * Note - 좌측 탭 기반 노트 (learn/change/research)
 */
export interface Note {
  id: string; // UUID
  project_id: string; // FK to Project
  type: NoteType;
  title: string;
  content: Record<string, unknown>; // JSONB - 유연한 콘텐츠 구조
  tags: string[]; // Array - 태그
  is_pinned: boolean;
  is_archived: boolean;
  created_at: Date;
  updated_at: Date;
}

/**
 * Media - 첨부 미디어 (project/note 연결)
 */
export interface Media {
  id: string; // UUID
  target_type: TargetType; // project | note
  target_id: string; // FK to Project or Note
  original_name: string;
  file_path: string;
  file_size: number; // bytes
  mime_type: string;
  type: MediaType;
  width?: number; // 이미지/비디오용
  height?: number; // 이미지/비디오용
  is_public: boolean;
  alt_text?: string; // 접근성용
  created_at: Date;
  updated_at: Date;
}

// =============================================================================
// Database Relations (참조 무결성)
// =============================================================================

/**
 * User와 관련된 엔티티들
 */
export interface UserWithRelations extends User {
  auth_accounts?: AuthAccount[];
  sessions?: Session[];
  projects?: Project[];
}

/**
 * Project와 관련된 엔티티들
 */
export interface ProjectWithRelations extends Project {
  owner: User;
  github_repository?: GithubRepository;
  notes?: Note[];
  media?: Media[];
}

/**
 * Note와 관련된 엔티티들
 */
export interface NoteWithRelations extends Note {
  project: Project;
  media?: Media[];
}

// =============================================================================
// API Request/Response Types
// =============================================================================

/**
 * 표준 API 응답 형식
 */
export interface SuccessResponse<T> {
  success: true;
  data: T;
  meta?: {
    total?: number;
    page?: number;
    pageSize?: number;
    totalPages?: number;
  };
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: string;
  path: string;
}

export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

// =============================================================================
// Create/Update DTOs
// =============================================================================

/**
 * User 생성/수정 DTO
 */
export interface CreateUserDto {
  email: string;
  name: string;
  bio?: string;
  avatar_url?: string;
  github_username?: string;
  role?: UserRole;
}

export type UpdateUserDto = Partial<CreateUserDto>;

/**
 * Project 생성/수정 DTO
 */
export interface CreateProjectDto {
  slug: string;
  title: string;
  description?: string;
  content?: Record<string, unknown>;
  tech_stack?: string[];
  categories?: string[];
  tags?: string[];
  status?: ProjectStatus;
  visibility?: ProjectVisibility;
  featured?: boolean;
}

export type UpdateProjectDto = Partial<CreateProjectDto>;

/**
 * Note 생성/수정 DTO
 */
export interface CreateNoteDto {
  project_id: string;
  type: NoteType;
  title: string;
  content?: Record<string, unknown>;
  tags?: string[];
  is_pinned?: boolean;
}

export type UpdateNoteDto = Partial<Omit<CreateNoteDto, 'project_id'>>;

/**
 * Media 업로드 DTO
 */
export interface CreateMediaDto {
  target_type: TargetType;
  target_id: string;
  original_name: string;
  file_size: number;
  mime_type: string;
  type: MediaType;
  width?: number;
  height?: number;
  is_public?: boolean;
  alt_text?: string;
}

// =============================================================================
// Filter/Query Types
// =============================================================================

/**
 * 페이지네이션 파라미터
 */
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Project 필터링 파라미터
 */
export interface ProjectFilters extends PaginationParams {
  status?: ProjectStatus;
  visibility?: ProjectVisibility;
  featured?: boolean;
  tech_stack?: string[];
  categories?: string[];
  tags?: string[];
  owner_id?: string;
  search?: string;
}

/**
 * Note 필터링 파라미터
 */
export interface NoteFilters extends PaginationParams {
  project_id?: string;
  type?: NoteType;
  tags?: string[];
  is_pinned?: boolean;
  is_archived?: boolean;
  search?: string;
}

/**
 * 검색 파라미터
 */
export interface SearchParams {
  query: string;
  type?: 'projects' | 'notes' | 'users' | 'all';
  filters?: Record<string, unknown>;
  limit?: number;
  offset?: number;
}

// =============================================================================
// Utility Types
// =============================================================================

/**
 * 데이터베이스 타임스탬프 필드
 */
export interface Timestamps {
  created_at: Date;
  updated_at: Date;
}

/**
 * UUID 기본키
 */
export interface WithId {
  id: string;
}

/**
 * 기본 엔티티 타입 (ID + 타임스탬프)
 */
export type BaseEntity = WithId & Timestamps;