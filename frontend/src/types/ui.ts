/**
 * Portfolio Manager UI Types
 * React 컴포넌트, 상태 관리, UI 인터랙션을 위한 타입 정의
 */

import { ReactNode } from 'react';
import {
  User,
  Project,
  Note,
  ProjectStatus,
  ProjectVisibility,
  NoteType,
  ProjectWithRelations,
  NoteWithRelations
} from './database';

// =============================================================================
// Common UI Types
// =============================================================================

export interface BaseComponentProps {
  className?: string;
  children?: ReactNode;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export interface SortState {
  field: string;
  direction: 'asc' | 'desc';
}

export interface FilterState {
  [key: string]: unknown;
}

// =============================================================================
// Navigation & Layout Types
// =============================================================================

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon?: string;
  badge?: string | number;
  active?: boolean;
  children?: NavigationItem[];
}

export interface SidebarProps extends BaseComponentProps {
  isOpen: boolean;
  onToggle: () => void;
  navigation: NavigationItem[];
}

export interface HeaderProps extends BaseComponentProps {
  user?: User;
  onMenuToggle: () => void;
  onUserMenuToggle: () => void;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps extends BaseComponentProps {
  items: BreadcrumbItem[];
  separator?: ReactNode;
}

// =============================================================================
// Form Types
// =============================================================================

export interface FormFieldError {
  message: string;
  type?: string;
}

export interface FormState<T = Record<string, unknown>> {
  values: T;
  errors: Record<keyof T, FormFieldError | undefined>;
  touched: Record<keyof T, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

export interface InputProps extends BaseComponentProps {
  name: string;
  label?: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select';
  value?: string | number;
  defaultValue?: string | number;
  required?: boolean;
  disabled?: boolean;
  error?: FormFieldError;
  onChange?: (value: string | number) => void;
  onBlur?: () => void;
}

export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

export interface SelectProps extends Omit<InputProps, 'type'> {
  options: SelectOption[];
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
}

// =============================================================================
// Project Management Types
// =============================================================================

export interface ProjectFormData {
  slug: string;
  title: string;
  description?: string;
  content?: Record<string, unknown>;
  tech_stack: string[];
  categories: string[];
  tags: string[];
  status: ProjectStatus;
  visibility: ProjectVisibility;
  featured: boolean;
  github_url?: string;
}

export interface ProjectCardProps extends BaseComponentProps {
  project: ProjectWithRelations;
  variant?: 'default' | 'compact' | 'detailed';
  showActions?: boolean;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
  onToggleFeatured?: (project: Project) => void;
  onVisibilityChange?: (project: Project, visibility: ProjectVisibility) => void;
}

export interface ProjectListProps extends BaseComponentProps {
  projects: ProjectWithRelations[];
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  variant?: 'grid' | 'list';
  showFilters?: boolean;
  showPagination?: boolean;
  onProjectSelect?: (project: Project) => void;
  onProjectEdit?: (project: Project) => void;
  onProjectDelete?: (project: Project) => void;
}

export interface ProjectFiltersProps extends BaseComponentProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onReset: () => void;
  availableTags?: string[];
  availableTechStack?: string[];
  availableCategories?: string[];
}

// =============================================================================
// Note System Types
// =============================================================================

export interface NoteFormData {
  title: string;
  type: NoteType;
  content?: Record<string, unknown>;
  tags: string[];
  is_pinned: boolean;
}

export interface NoteTabProps extends BaseComponentProps {
  type: NoteType;
  count: number;
  active: boolean;
  onClick: (type: NoteType) => void;
}

export interface NoteListProps extends BaseComponentProps {
  notes: NoteWithRelations[];
  selectedType: NoteType;
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  onNoteSelect?: (note: Note) => void;
  onNoteEdit?: (note: Note) => void;
  onNoteDelete?: (note: Note) => void;
  onNotePin?: (note: Note) => void;
}

export interface NoteEditorProps extends BaseComponentProps {
  note?: Note;
  projectId: string;
  onSave: (data: NoteFormData) => Promise<void>;
  onCancel: () => void;
  autosave?: boolean;
  autosaveDelay?: number;
}

export interface NoteSidebarProps extends BaseComponentProps {
  projectId: string;
  selectedType: NoteType;
  selectedNoteId?: string;
  onTypeChange: (type: NoteType) => void;
  onNoteSelect: (noteId: string) => void;
  onNewNote: (type: NoteType) => void;
}

// =============================================================================
// Media & File Upload Types
// =============================================================================

export interface FileUploadProps extends BaseComponentProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number;
  maxFiles?: number;
  onUpload: (files: File[]) => Promise<void>;
  onProgress?: (progress: number) => void;
  onError?: (error: string) => void;
  dragAndDrop?: boolean;
  showPreview?: boolean;
}

export interface MediaGalleryProps extends BaseComponentProps {
  media: Record<string, unknown>[]; // Media[] from database types
  selectable?: boolean;
  selectedIds?: string[];
  onSelect?: (mediaIds: string[]) => void;
  onDelete?: (mediaId: string) => void;
  onPreview?: (media: Record<string, unknown>) => void;
}

export interface MediaPreviewProps extends BaseComponentProps {
  media: Record<string, unknown>; // Media from database types
  isOpen: boolean;
  onClose: () => void;
  onDelete?: () => void;
  onDownload?: () => void;
}

// =============================================================================
// Search & Filter Types
// =============================================================================

export interface SearchBarProps extends BaseComponentProps {
  value?: string;
  placeholder?: string;
  onSearch: (query: string) => void;
  onClear?: () => void;
  showSuggestions?: boolean;
  suggestions?: SearchSuggestion[];
  loading?: boolean;
}

export interface SearchSuggestion {
  type: 'project' | 'note' | 'tag' | 'tech_stack';
  text: string;
  count?: number;
  icon?: string;
}

export interface SearchResultsProps extends BaseComponentProps {
  query: string;
  results: {
    projects?: ProjectWithRelations[];
    notes?: NoteWithRelations[];
    users?: User[];
  };
  loading?: boolean;
  error?: string;
  onResultClick: (type: string, id: string) => void;
}

// =============================================================================
// Modal & Dialog Types
// =============================================================================

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closable?: boolean;
  backdrop?: boolean;
}

export interface ConfirmDialogProps extends BaseComponentProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  onConfirm: () => void;
  onCancel: () => void;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  actions?: ToastAction[];
}

export interface ToastAction {
  label: string;
  onClick: () => void;
}

// =============================================================================
// Dashboard & Analytics Types
// =============================================================================

export interface DashboardStats {
  totalProjects: number;
  totalNotes: number;
  totalViews: number;
  totalLikes: number;
  publishedProjects: number;
  draftProjects: number;
  featuredProjects: number;
}

export interface DashboardProps extends BaseComponentProps {
  user: User;
  stats: DashboardStats;
  recentProjects: ProjectWithRelations[];
  recentNotes: NoteWithRelations[];
  onProjectClick: (project: Project) => void;
  onNoteClick: (note: Note) => void;
}

export interface AnalyticsChartProps extends BaseComponentProps {
  data: Record<string, unknown>[]; // Chart data
  type: 'line' | 'bar' | 'pie' | 'area';
  title?: string;
  description?: string;
  height?: number;
  loading?: boolean;
}

// =============================================================================
// State Management Types (Zustand)
// =============================================================================

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (provider: 'github' | 'google') => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

export interface ProjectState {
  projects: ProjectWithRelations[];
  selectedProject: ProjectWithRelations | null;
  filters: FilterState;
  pagination: PaginationState;
  sort: SortState;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchProjects: (params?: Record<string, unknown>) => Promise<void>;
  createProject: (data: ProjectFormData) => Promise<void>;
  updateProject: (id: string, data: Partial<ProjectFormData>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  setSelectedProject: (project: ProjectWithRelations | null) => void;
  setFilters: (filters: FilterState) => void;
  setPagination: (pagination: Partial<PaginationState>) => void;
  setSort: (sort: SortState) => void;
  clearError: () => void;
}

export interface NoteState {
  notes: NoteWithRelations[];
  selectedNote: NoteWithRelations | null;
  selectedType: NoteType;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchNotes: (projectId: string, type?: NoteType) => Promise<void>;
  createNote: (projectId: string, data: NoteFormData) => Promise<void>;
  updateNote: (id: string, data: Partial<NoteFormData>) => Promise<void>;
  deleteNote: (id: string) => Promise<void>;
  setSelectedNote: (note: NoteWithRelations | null) => void;
  setSelectedType: (type: NoteType) => void;
  clearError: () => void;
}

export interface UIState {
  sidebarOpen: boolean;
  userMenuOpen: boolean;
  searchQuery: string;
  toasts: ToastMessage[];
  modals: Record<string, boolean>;
  
  // Actions
  toggleSidebar: () => void;
  toggleUserMenu: () => void;
  setSearchQuery: (query: string) => void;
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;
  openModal: (id: string) => void;
  closeModal: (id: string) => void;
}

// =============================================================================
// Router & Navigation Types
// =============================================================================

export interface RouteParams {
  [key: string]: string | string[] | undefined;
}

export interface PageProps<T extends RouteParams = Record<string, never>> {
  params: T;
  searchParams?: { [key: string]: string | string[] | undefined };
}

export interface LayoutProps {
  children: ReactNode;
  params?: RouteParams;
}

// =============================================================================
// Theme & Styling Types
// =============================================================================

export interface ThemeConfig {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    error: string;
    warning: string;
    success: string;
    info: string;
  };
  fonts: {
    sans: string;
    mono: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  breakpoints: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

export type ThemeMode = 'light' | 'dark' | 'system';