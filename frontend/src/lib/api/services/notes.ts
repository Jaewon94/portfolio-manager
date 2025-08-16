/**
 * Notes Service - 노트 관련 API 호출
 */

import { ApiClient, ApiError } from '../client';
import {
  GetNotesRequest,
  GetNotesResponse,
  GetNoteRequest,
  GetNoteResponse,
  CreateNoteRequest,
  CreateNoteResponse,
  UpdateNoteRequest,
  UpdateNoteResponse,
  DeleteNoteResponse,
  NoteWithRelations,
  NoteType
} from '@/types';

export class NotesService {
  constructor(private client: ApiClient) {}

  /**
   * 프로젝트의 노트 목록 조회
   */
  async getNotes(projectId: string, params?: Omit<GetNotesRequest, 'project_id'>): Promise<GetNotesResponse> {
    try {
      const queryParams = { project_id: projectId, ...params };
      return await this.client.get<GetNotesResponse>(`/api/projects/${projectId}/notes`, queryParams);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_NOTES_FAILED',
        'Failed to fetch notes',
        500,
        { originalError: error, projectId }
      );
    }
  }

  /**
   * 노트 상세 조회
   */
  async getNote(id: string, options?: Omit<GetNoteRequest, 'id'>): Promise<GetNoteResponse> {
    try {
      const params = options ? { ...options } : undefined;
      return await this.client.get<GetNoteResponse>(`/api/notes/${id}`, params);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_NOTE_FAILED',
        'Failed to fetch note',
        500,
        { originalError: error, noteId: id }
      );
    }
  }

  /**
   * 노트 생성
   */
  async createNote(projectId: string, data: Omit<CreateNoteRequest, 'project_id'>): Promise<CreateNoteResponse> {
    try {
      const noteData = { project_id: projectId, ...data };
      return await this.client.post<CreateNoteResponse>(`/api/projects/${projectId}/notes`, noteData);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'CREATE_NOTE_FAILED',
        'Failed to create note',
        500,
        { originalError: error, projectId }
      );
    }
  }

  /**
   * 노트 수정
   */
  async updateNote(id: string, data: Omit<UpdateNoteRequest, 'id'>): Promise<UpdateNoteResponse> {
    try {
      return await this.client.patch<UpdateNoteResponse>(`/api/notes/${id}`, data);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'UPDATE_NOTE_FAILED',
        'Failed to update note',
        500,
        { originalError: error, noteId: id }
      );
    }
  }

  /**
   * 노트 삭제
   */
  async deleteNote(id: string): Promise<DeleteNoteResponse> {
    try {
      return await this.client.delete<DeleteNoteResponse>(`/api/notes/${id}`);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'DELETE_NOTE_FAILED',
        'Failed to delete note',
        500,
        { originalError: error, noteId: id }
      );
    }
  }

  /**
   * 노트 타입별 조회
   */
  async getNotesByType(projectId: string, type: NoteType): Promise<NoteWithRelations[]> {
    try {
      const response = await this.getNotes(projectId, { type });
      return response.notes;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_NOTES_BY_TYPE_FAILED',
        'Failed to fetch notes by type',
        500,
        { originalError: error, projectId, type }
      );
    }
  }

  /**
   * 노트 고정/고정 해제
   */
  async toggleNotePinned(id: string, is_pinned: boolean): Promise<UpdateNoteResponse> {
    return this.updateNote(id, { is_pinned });
  }

  /**
   * 노트 보관/보관 해제
   */
  async toggleNoteArchived(id: string, is_archived: boolean): Promise<UpdateNoteResponse> {
    return this.updateNote(id, { is_archived });
  }

  /**
   * 고정된 노트 목록 조회
   */
  async getPinnedNotes(projectId: string): Promise<NoteWithRelations[]> {
    try {
      const response = await this.getNotes(projectId, { is_pinned: true });
      return response.notes;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_PINNED_NOTES_FAILED',
        'Failed to fetch pinned notes',
        500,
        { originalError: error, projectId }
      );
    }
  }

  /**
   * 노트 검색 (프로젝트 내)
   */
  async searchNotes(projectId: string, query: string): Promise<NoteWithRelations[]> {
    try {
      const response = await this.getNotes(projectId, { search: query });
      return response.notes;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'SEARCH_NOTES_FAILED',
        'Failed to search notes',
        500,
        { originalError: error, projectId, query }
      );
    }
  }

  /**
   * 노트에 태그 추가
   */
  async addNoteTag(id: string, tag: string): Promise<UpdateNoteResponse> {
    try {
      const note = await this.getNote(id);
      const currentTags = note.note.tags || [];
      
      if (!currentTags.includes(tag)) {
        const updatedTags = [...currentTags, tag];
        return await this.updateNote(id, { tags: updatedTags });
      }
      
      return { note: note.note };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'ADD_NOTE_TAG_FAILED',
        'Failed to add note tag',
        500,
        { originalError: error, noteId: id, tag }
      );
    }
  }

  /**
   * 노트에서 태그 제거
   */
  async removeNoteTag(id: string, tag: string): Promise<UpdateNoteResponse> {
    try {
      const note = await this.getNote(id);
      const currentTags = note.note.tags || [];
      const updatedTags = currentTags.filter(t => t !== tag);
      
      return await this.updateNote(id, { tags: updatedTags });
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'REMOVE_NOTE_TAG_FAILED',
        'Failed to remove note tag',
        500,
        { originalError: error, noteId: id, tag }
      );
    }
  }
}