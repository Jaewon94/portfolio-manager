// 사용자 타입
export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  bio?: string
  website_url?: string
  github_username?: string
  linkedin_url?: string
  role: 'user' | 'admin'
  is_verified: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

// 프로젝트 타입
export interface Project {
  id: string
  owner_id: string
  slug: string
  title: string
  description?: string
  content?: Record<string, unknown> // JSONB 형식
  tech_stack: string[]
  categories: string[]
  tags: string[]
  status: 'draft' | 'active' | 'archived' | 'deleted'
  visibility: 'public' | 'private' | 'unlisted'
  featured: boolean
  view_count: number
  like_count: number
  created_at: string
  updated_at: string
  published_at?: string
  owner?: {
    id: string
    name: string
    avatar_url?: string
    bio?: string
  }
  github_repository?: GithubRepository
  media?: Media[]
  note_count?: number
  note_summary?: {
    learn: number
    change: number
    research: number
  }
}

// GitHub 저장소 타입
export interface GithubRepository {
  id: string
  project_id: string
  github_url: string
  repository_name: string
  stars: number
  forks: number
  watchers: number
  language?: string
  license?: string
  is_private: boolean
  is_fork: boolean
  last_commit_sha?: string
  last_commit_message?: string
  last_commit_date?: string
  last_synced_at: string
  sync_error_message?: string
  is_sync_enabled: boolean
  created_at: string
  updated_at: string
}

// 노트 타입
export interface Note {
  id: string
  project_id: string
  type: 'learn' | 'change' | 'research'
  title: string
  content: Record<string, unknown> // JSONB 형식
  tags: string[]
  is_pinned: boolean
  is_archived: boolean
  created_at: string
  updated_at: string
  project?: {
    id: string
    title: string
    slug: string
  }
  media?: Media[]
}

// 미디어 타입
export interface Media {
  id: string
  target_type: 'project' | 'note'
  target_id: string
  original_name: string
  file_name: string
  file_path: string
  file_size: number
  mime_type: string
  type: 'image' | 'video' | 'document' | 'archive'
  width?: number
  height?: number
  duration?: number
  is_public: boolean
  alt_text?: string
  created_at: string
  updated_at: string
}

// 검색 결과 타입
export interface SearchResult {
  projects?: Array<Project & {
    highlight: {
      title?: string
      description?: string
    }
    type: 'project'
  }>
  notes?: Array<Note & {
    highlight: {
      title?: string
      content?: string
    }
    type: 'note'
    note_type: string
  }>
  users?: Array<User & {
    highlight: {
      name?: string
      bio?: string
    }
    type: 'user'
    project_count: number
  }>
}

// 폼 타입들
export interface CreateProjectForm {
  title: string
  description?: string
  slug: string
  content?: Record<string, unknown>
  tech_stack: string[]
  categories: string[]
  tags: string[]
  visibility: 'public' | 'private' | 'unlisted'
  github_url?: string
}

export interface CreateNoteForm {
  type: 'learn' | 'change' | 'research'
  title: string
  content: Record<string, unknown>
  tags: string[]
  is_pinned?: boolean
}

export interface UpdateUserForm {
  name: string
  bio?: string
  website_url?: string
  github_username?: string
  linkedin_url?: string
}

// API 응답 타입들
export interface PaginationMeta {
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ApiListResponse<T> {
  success: true
  data: T[]
  meta: PaginationMeta
}

export interface ApiSingleResponse<T> {
  success: true
  data: T
  message?: string
}

export interface ApiErrorResponse {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
  timestamp: string
  path: string
}