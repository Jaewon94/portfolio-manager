/**
 * Dashboard API Service
 * 대시보드 통계 및 요약 정보 API
 */

import { apiClient } from '../client';
import { GetProjectsResponse } from '@/types/api';

// 대시보드 통계 타입
export interface DashboardStats {
  total_projects: number;
  completed_projects: number;
  active_projects: number;
  pending_projects: number;
  total_notes: number;
  public_projects: number;
  private_projects: number;
  total_views: number;
  total_likes: number;
}

// 최근 프로젝트 타입
export interface RecentProject {
  id: number;
  title: string;
  description: string;
  status: 'draft' | 'published' | 'archived';
  updated_at: string;
  view_count: number;
  like_count: number;
  visibility: 'public' | 'private' | 'unlisted';
}

// 최근 활동 타입
export interface RecentActivity {
  id: number;
  type: 'project_created' | 'project_updated' | 'project_completed' | 'note_created';
  title: string;
  description: string;
  created_at: string;
  project_id?: number;
  project_title?: string;
}

// Dashboard API 응답 타입
export interface DashboardResponse {
  stats: DashboardStats;
  recent_projects: RecentProject[];
  recent_activities: RecentActivity[];
}

export class DashboardService {
  /**
   * 대시보드 전체 데이터 조회
   * 전용 엔드포인트가 없으면 기존 API들을 조합해서 구성
   */
  async getDashboardData(): Promise<DashboardResponse> {
    try {
      console.log('🔄 대시보드 데이터 요청 시작...');
      
      // 먼저 전용 엔드포인트 시도
      try {
        const response = await apiClient.get<DashboardResponse>('/dashboard');
        console.log('✅ 대시보드 전용 API 응답:', response);
        return response;
      } catch {
        console.log('⚠️ 대시보드 전용 API가 없음, 기존 API들로 구성...');
        
        // 기존 API들을 조합해서 대시보드 데이터 구성
        const [projectsResponse] = await Promise.all([
          apiClient.get<GetProjectsResponse>('/projects', { page: 1, page_size: 100 })
        ]);
        
        const projects = projectsResponse.projects || [];
        
        // 통계 계산
        const stats: DashboardStats = {
          total_projects: projects.length,
          completed_projects: projects.filter(p => p.status === 'published').length,
          active_projects: projects.filter(p => p.status === 'draft').length,
          pending_projects: projects.filter(p => p.status === 'archived').length,
          total_notes: 0, // 노트 API로 별도 조회 필요
          public_projects: projects.filter(p => p.visibility === 'public').length,
          private_projects: projects.filter(p => p.visibility === 'private').length,
          total_views: projects.reduce((sum, p) => sum + (p.view_count || 0), 0),
          total_likes: projects.reduce((sum, p) => sum + (p.like_count || 0), 0),
        };
        
        // 최근 프로젝트 (최근 업데이트 순으로 5개)
        const recent_projects: RecentProject[] = projects
          .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
          .slice(0, 5)
          .map(p => ({
            id: p.id,
            title: p.title,
            description: p.description || '',
            status: p.status,
            updated_at: p.updated_at.toString(),
            view_count: p.view_count || 0,
            like_count: p.like_count || 0,
            visibility: p.visibility
          }));
        
        // 최근 활동 (프로젝트 업데이트 기반으로 생성)
        const recent_activities: RecentActivity[] = projects
          .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
          .slice(0, 5)
          .map((p, index) => ({
            id: index + 1,
            type: p.status === 'published' ? 'project_completed' : 'project_updated',
            title: p.title,
            description: `${p.title} 프로젝트가 업데이트되었습니다`,
            created_at: p.updated_at.toString(),
            project_id: p.id,
            project_title: p.title
          }));
        
        const fallbackResponse: DashboardResponse = {
          stats,
          recent_projects,
          recent_activities
        };
        
        console.log('✅ 기존 API로 구성된 대시보드 데이터:', fallbackResponse);
        return fallbackResponse;
      }
    } catch (error) {
      console.error('❌ 대시보드 데이터 조회 완전 실패:', error);
      throw error;
    }
  }

  /**
   * 통계 데이터만 조회
   */
  async getStats(): Promise<DashboardStats> {
    try {
      console.log('🔄 대시보드 통계 요청 시작...');
      
      const response = await apiClient.get<DashboardStats>('/dashboard/stats');
      
      console.log('✅ 대시보드 통계 응답:', response);
      return response;
    } catch (error) {
      console.error('❌ 대시보드 통계 조회 실패:', error);
      throw error;
    }
  }

  /**
   * 최근 프로젝트만 조회
   */
  async getRecentProjects(limit: number = 5): Promise<RecentProject[]> {
    try {
      console.log('🔄 최근 프로젝트 요청 시작...');
      
      const response = await apiClient.get<RecentProject[]>('/dashboard/recent-projects', {
        limit
      });
      
      console.log('✅ 최근 프로젝트 응답:', response);
      return response;
    } catch (error) {
      console.error('❌ 최근 프로젝트 조회 실패:', error);
      throw error;
    }
  }

  /**
   * 최근 활동만 조회
   */
  async getRecentActivities(limit: number = 5): Promise<RecentActivity[]> {
    try {
      console.log('🔄 최근 활동 요청 시작...');
      
      const response = await apiClient.get<RecentActivity[]>('/dashboard/recent-activities', {
        limit
      });
      
      console.log('✅ 최근 활동 응답:', response);
      return response;
    } catch (error) {
      console.error('❌ 최근 활동 조회 실패:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 생성
export const dashboardService = new DashboardService();
export default dashboardService;