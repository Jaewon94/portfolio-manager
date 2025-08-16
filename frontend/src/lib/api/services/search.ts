/**
 * Search Service - 검색 관련 API 호출
 */

import { ApiClient, ApiError } from '../client';
import {
  SearchRequest,
  SearchResponse,
  AutocompleteRequest,
  AutocompleteResponse,
  ProjectWithRelations,
  NoteWithRelations,
  User
} from '@/types';

export class SearchService {
  constructor(private client: ApiClient) {}

  /**
   * 전역 검색
   */
  async search(params: SearchRequest): Promise<SearchResponse> {
    try {
      return await this.client.get<SearchResponse>('/api/search', params);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'SEARCH_FAILED',
        'Search failed',
        500,
        { originalError: error, query: params.query }
      );
    }
  }

  /**
   * 자동완성 검색
   */
  async autocomplete(params: AutocompleteRequest): Promise<AutocompleteResponse> {
    try {
      return await this.client.get<AutocompleteResponse>('/api/search/autocomplete', params);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'AUTOCOMPLETE_FAILED',
        'Autocomplete failed',
        500,
        { originalError: error, query: params.query }
      );
    }
  }

  /**
   * 프로젝트 검색
   */
  async searchProjects(query: string, filters?: {
    tags?: string[];
    tech_stack?: string[];
    categories?: string[];
    status?: string;
    visibility?: string;
  }): Promise<ProjectWithRelations[]> {
    try {
      const params: SearchRequest = {
        query,
        type: 'projects' as const,
        ...filters
      };
      
      const response = await this.search(params);
      return response.results.projects || [];
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'SEARCH_PROJECTS_FAILED',
        'Project search failed',
        500,
        { originalError: error, query }
      );
    }
  }

  /**
   * 노트 검색
   */
  async searchNotes(query: string, filters?: {
    project_id?: string;
    type?: string;
    tags?: string[];
    is_pinned?: boolean;
  }): Promise<NoteWithRelations[]> {
    try {
      const params: SearchRequest = {
        query,
        ...filters,
        type: 'notes' as const
      };
      
      const response = await this.search(params);
      return response.results.notes || [];
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'SEARCH_NOTES_FAILED',
        'Note search failed',
        500,
        { originalError: error, query }
      );
    }
  }

  /**
   * 사용자 검색
   */
  async searchUsers(query: string): Promise<User[]> {
    try {
      const params: SearchRequest = {
        query,
        type: 'users' as const
      };
      
      const response = await this.search(params);
      return response.results.users || [];
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'SEARCH_USERS_FAILED',
        'User search failed',
        500,
        { originalError: error, query }
      );
    }
  }

  /**
   * 태그 자동완성
   */
  async autocompleteTags(query: string, limit = 10): Promise<string[]> {
    try {
      const response = await this.autocomplete({
        query,
        type: 'tags' as const,
        limit
      });
      
      return response.suggestions
        .filter(s => s.type === 'tag')
        .map(s => s.text);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'AUTOCOMPLETE_TAGS_FAILED',
        'Tag autocomplete failed',
        500,
        { originalError: error, query }
      );
    }
  }

  /**
   * 기술 스택 자동완성
   */
  async autocompleteTechStack(query: string, limit = 10): Promise<string[]> {
    try {
      const response = await this.autocomplete({
        query,
        type: 'tech_stack' as const,
        limit
      });
      
      return response.suggestions
        .filter(s => s.type === 'tech_stack')
        .map(s => s.text);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'AUTOCOMPLETE_TECH_STACK_FAILED',
        'Tech stack autocomplete failed',
        500,
        { originalError: error, query }
      );
    }
  }

  /**
   * 프로젝트 내 노트 검색
   */
  async searchNotesInProject(projectId: string, query: string): Promise<NoteWithRelations[]> {
    return this.searchNotes(query, { project_id: projectId });
  }

  /**
   * 고급 검색 (다중 필터)
   */
  async advancedSearch(params: {
    query: string;
    projects?: {
      tags?: string[];
      tech_stack?: string[];
      categories?: string[];
      status?: string;
      visibility?: string;
    };
    notes?: {
      project_id?: string;
      type?: string;
      tags?: string[];
    };
    users?: boolean;
  }): Promise<{
    projects: ProjectWithRelations[];
    notes: NoteWithRelations[];
    users: User[];
  }> {
    try {
      const searchPromises = [];
      
      // 프로젝트 검색
      if (params.projects !== undefined) {
        searchPromises.push(
          this.searchProjects(params.query, params.projects)
        );
      } else {
        searchPromises.push(Promise.resolve([]));
      }
      
      // 노트 검색
      if (params.notes !== undefined) {
        searchPromises.push(
          this.searchNotes(params.query, params.notes)
        );
      } else {
        searchPromises.push(Promise.resolve([]));
      }
      
      // 사용자 검색
      if (params.users) {
        searchPromises.push(
          this.searchUsers(params.query)
        );
      } else {
        searchPromises.push(Promise.resolve([]));
      }
      
      const [projects, notes, users] = await Promise.all(searchPromises);
      
      return {
        projects: projects as ProjectWithRelations[],
        notes: notes as NoteWithRelations[],
        users: users as User[]
      };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'ADVANCED_SEARCH_FAILED',
        'Advanced search failed',
        500,
        { originalError: error, query: params.query }
      );
    }
  }

  /**
   * 검색 결과 하이라이트 제거
   */
  stripHighlight(text: string): string {
    return text.replace(/<\/?mark>/g, '');
  }

  /**
   * 검색어 제안
   */
  async getSearchSuggestions(query: string): Promise<{
    projects: string[];
    tags: string[];
    techStack: string[];
  }> {
    try {
      const [projects, tags, techStack] = await Promise.all([
        this.autocomplete({ query, type: 'projects' as const, limit: 5 }),
        this.autocompleteTags(query, 5),
        this.autocompleteTechStack(query, 5)
      ]);
      
      return {
        projects: projects.suggestions.map(s => s.text),
        tags,
        techStack
      };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_SEARCH_SUGGESTIONS_FAILED',
        'Failed to get search suggestions',
        500,
        { originalError: error, query }
      );
    }
  }
}