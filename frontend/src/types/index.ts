/**
 * Portfolio Manager Types Index
 * 모든 타입 정의를 중앙에서 관리하는 엔트리 포인트
 */

// Database Types
export * from './database';

// API Types
export * from './api';

// UI Types
export * from './ui';

// Type Guards and Utilities
export const isUser = (obj: unknown): obj is import('./database').User => {
  return obj !== null && typeof obj === 'object' && 'id' in obj && 'email' in obj && 
         typeof (obj as Record<string, unknown>).id === 'string' && typeof (obj as Record<string, unknown>).email === 'string';
};

export const isProject = (obj: unknown): obj is import('./database').Project => {
  return obj !== null && typeof obj === 'object' && 'id' in obj && 'title' in obj &&
         typeof (obj as Record<string, unknown>).id === 'string' && typeof (obj as Record<string, unknown>).title === 'string';
};

export const isNote = (obj: unknown): obj is import('./database').Note => {
  return obj !== null && typeof obj === 'object' && 'id' in obj && 'title' in obj && 'project_id' in obj &&
         typeof (obj as Record<string, unknown>).id === 'string' && typeof (obj as Record<string, unknown>).title === 'string' && 
         typeof (obj as Record<string, unknown>).project_id === 'string';
};

export const isSuccessResponse = <T>(response: unknown): response is import('./database').SuccessResponse<T> => {
  return response !== null && typeof response === 'object' && 'success' in response && 'data' in response &&
         (response as Record<string, unknown>).success === true && (response as Record<string, unknown>).data !== undefined;
};

export const isErrorResponse = (response: unknown): response is import('./database').ErrorResponse => {
  return response !== null && typeof response === 'object' && 'success' in response && 'error' in response &&
         (response as Record<string, unknown>).success === false && (response as Record<string, unknown>).error !== undefined;
};