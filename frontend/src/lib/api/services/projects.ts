/**
 * Projects Service - 프로젝트 관련 API 호출
 */

import { ApiClient, ApiError } from '../client';
import {
  GetProjectsRequest,
  GetProjectsResponse,
  GetProjectRequest,
  GetProjectResponse,
  CreateProjectRequest,
  CreateProjectResponse,
  UpdateProjectRequest,
  UpdateProjectResponse,
  DeleteProjectRequest,
  DeleteProjectResponse,
  Project,
  ProjectWithRelations,
  ProjectVisibility
} from '@/types';

export class ProjectsService {
  constructor(private client: ApiClient) {}

  /**
   * 프로젝트 목록 조회
   */
  async getProjects(params?: GetProjectsRequest): Promise<GetProjectsResponse> {
    try {
      return await this.client.get<GetProjectsResponse>('/projects/', params);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_PROJECTS_FAILED',
        'Failed to fetch projects',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 프로젝트 상세 조회
   */
  async getProject(id: string, options?: Omit<GetProjectRequest, 'id'>): Promise<GetProjectResponse> {
    try {
      const params = options ? { ...options } : undefined;
      return await this.client.get<GetProjectResponse>(`/projects/${id}/`, params);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_PROJECT_FAILED',
        'Failed to fetch project',
        500,
        { originalError: error, projectId: id }
      );
    }
  }

  /**
   * 프로젝트 생성
   */
  async createProject(data: CreateProjectRequest): Promise<CreateProjectResponse> {
    try {
      return await this.client.post<CreateProjectResponse>('/projects/', data);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'CREATE_PROJECT_FAILED',
        'Failed to create project',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 프로젝트 수정
   */
  async updateProject(id: string, data: Omit<UpdateProjectRequest, 'id'>): Promise<UpdateProjectResponse> {
    try {
      return await this.client.patch<UpdateProjectResponse>(`/projects/${id}/`, data);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'UPDATE_PROJECT_FAILED',
        'Failed to update project',
        500,
        { originalError: error, projectId: id }
      );
    }
  }

  /**
   * 프로젝트 삭제
   */
  async deleteProject(id: string): Promise<DeleteProjectResponse> {
    try {
      return await this.client.delete<DeleteProjectResponse>(`/projects/${id}/`);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'DELETE_PROJECT_FAILED',
        'Failed to delete project',
        500,
        { originalError: error, projectId: id }
      );
    }
  }

  /**
   * 프로젝트 상태 변경 (발행/초안)
   */
  async updateProjectStatus(id: string, status: Project['status']): Promise<UpdateProjectResponse> {
    return this.updateProject(id, { status });
  }

  /**
   * 프로젝트 가시성 변경 (공개/비공개)
   */
  async updateProjectVisibility(id: string, visibility: Project['visibility']): Promise<UpdateProjectResponse> {
    return this.updateProject(id, { visibility });
  }

  /**
   * 프로젝트 추천 상태 토글
   */
  async toggleProjectFeatured(id: string, featured: boolean): Promise<UpdateProjectResponse> {
    return this.updateProject(id, { featured });
  }

  /**
   * 내 프로젝트 목록 조회 (인증 필요)
   */
  async getMyProjects(params?: Omit<GetProjectsRequest, 'owner_id'>): Promise<GetProjectsResponse> {
    try {
      return await this.client.get<GetProjectsResponse>('/projects/me/', params);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_MY_PROJECTS_FAILED',
        'Failed to fetch my projects',
        500,
        { originalError: error }
      );
    }
  }

  /**
   * 추천 프로젝트 목록 조회
   */
  async getFeaturedProjects(limit = 10): Promise<ProjectWithRelations[]> {
    try {
      const response = await this.getProjects({ 
        featured: true, 
        limit,
        visibility: ProjectVisibility.PUBLIC
      });
      return response.projects;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_FEATURED_PROJECTS_FAILED',
        'Failed to fetch featured projects',
        500,
        { originalError: error }
      );
    }
  }
}

// 기본 인스턴스 생성 및 export
import { apiClient } from '../client';

export const projectService = new ProjectsService(apiClient);