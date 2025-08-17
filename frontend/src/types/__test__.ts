/**
 * TypeScript 타입 정의 테스트
 * 컴파일 타임 타입 체크를 위한 간단한 테스트 파일
 */

import {
  CreateNoteDto,
  CreateProjectDto,
  GetProjectsResponse,
  // API Types
  LoginRequest,
  Note,
  NoteType,
  Project,
  ProjectStatus,
  ProjectVisibility,
  ProjectWithRelations,
  SearchResult,
  // Database Types
  User,
} from './api';
import { UserRole } from './database';

// 테스트 타입들 (기본값 사용)
interface ProjectFormData {
  slug: string;
  title: string;
  description: string;
  tech_stack: string[];
  categories: string[];
  tags: string[];
  status: ProjectStatus;
  visibility: ProjectVisibility;
  featured: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

// Type guards (기본 구현)
const isUser = (obj: unknown): obj is User => {
  return (
    typeof obj === 'object' && obj !== null && 'id' in obj && 'email' in obj
  );
};

const isProject = (obj: unknown): obj is Project => {
  return (
    typeof obj === 'object' && obj !== null && 'id' in obj && 'title' in obj
  );
};

const isNote = (obj: unknown): obj is Note => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'project_id' in obj
  );
};

const isSuccessResponse = (
  obj: unknown
): obj is { success: true; data: unknown } => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'success' in obj &&
    (obj as { success: unknown }).success === true
  );
};

const isErrorResponse = (
  obj: unknown
): obj is { success: false; error: unknown } => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'success' in obj &&
    (obj as { success: unknown }).success === false
  );
};

// =============================================================================
// Database Types 테스트
// =============================================================================

// User 타입 테스트
const testUser: User = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  bio: 'Test bio',
  github_username: 'testuser',
  role: UserRole.USER,
  is_verified: true,
  created_at: new Date(),
  updated_at: new Date(),
};

// Project 타입 테스트
const testProject: Project = {
  id: 2,
  owner_id: 1,
  slug: 'test-project',
  title: 'Test Project',
  description: 'Test project description',
  content: { type: 'html', body: '<p>Test content</p>' },
  tech_stack: ['TypeScript', 'React', 'Next.js'],
  categories: ['Web Development'],
  tags: ['frontend', 'typescript'],
  status: ProjectStatus.PUBLISHED,
  visibility: ProjectVisibility.PUBLIC,
  featured: false,
  view_count: 0,
  like_count: 0,
  created_at: new Date(),
  updated_at: new Date(),
};

// Note 타입 테스트
const testNote: Note = {
  id: 3,
  project_id: 2,
  type: NoteType.LEARN,
  title: 'Test Note',
  content: { type: 'markdown', body: '# Test note content' },
  tags: ['learning', 'typescript'],
  is_pinned: false,
  is_archived: false,
  created_at: new Date(),
  updated_at: new Date(),
};

// Relations 타입 테스트
const testProjectWithRelations: ProjectWithRelations = {
  ...testProject,
  owner: testUser,
  notes: [testNote],
  media: [],
};

// =============================================================================
// DTO Types 테스트
// =============================================================================

const testCreateProjectDto: CreateProjectDto = {
  slug: 'new-project',
  title: 'New Project',
  description: 'New project description',
  tech_stack: ['React'],
  status: ProjectStatus.DRAFT,
  visibility: ProjectVisibility.PRIVATE,
};

const testCreateNoteDto: CreateNoteDto = {
  project_id: 2,
  type: NoteType.CHANGE,
  title: 'New Note',
  content: { type: 'markdown', body: 'Content' },
  tags: ['change'],
};

// =============================================================================
// API Types 테스트
// =============================================================================

const testLoginRequest: LoginRequest = {
  provider: 'github',
  redirect_url: '/dashboard',
};

const testGetProjectsResponse: GetProjectsResponse = {
  projects: [testProjectWithRelations],
  pagination: {
    total: 1,
    page: 1,
    pageSize: 10,
    totalPages: 1,
  },
};

const testSearchResult: SearchResult = {
  projects: [
    {
      ...testProjectWithRelations,
      highlight: {
        title: '<mark>Test</mark> Project',
        description: '<mark>Test</mark> description',
      },
      type: 'project',
    },
  ],
  notes: [],
  users: [],
};

// =============================================================================
// UI Types 테스트
// =============================================================================

const testProjectFormData: ProjectFormData = {
  slug: 'form-project',
  title: 'Form Project',
  description: 'Created from form',
  tech_stack: ['Next.js'],
  categories: ['Web'],
  tags: ['form'],
  status: ProjectStatus.DRAFT,
  visibility: ProjectVisibility.PUBLIC,
  featured: false,
};

const testAuthState: AuthState = {
  user: testUser,
  isAuthenticated: true,
  isLoading: false,
  error: null,
  login: async () => {},
  logout: async () => {},
  refreshToken: async () => {},
  clearError: () => {},
};

// =============================================================================
// Type Guards 테스트
// =============================================================================

// Type guard 테스트
console.log('isUser test:', isUser(testUser)); // true
console.log('isProject test:', isProject(testProject)); // true
console.log('isNote test:', isNote(testNote)); // true

const successResponse = { success: true, data: testUser };
const errorResponse = {
  success: false,
  error: { code: 'ERR', message: 'Error' },
};

console.log('isSuccessResponse test:', isSuccessResponse(successResponse)); // true
console.log('isErrorResponse test:', isErrorResponse(errorResponse)); // true

// =============================================================================
// 컴파일 타임 테스트 완료
// =============================================================================

export const typeTests = {
  testUser,
  testProject,
  testNote,
  testProjectWithRelations,
  testCreateProjectDto,
  testCreateNoteDto,
  testLoginRequest,
  testGetProjectsResponse,
  testSearchResult,
  testProjectFormData,
  testAuthState,
};

console.log('TypeScript 타입 정의 테스트 완료');
