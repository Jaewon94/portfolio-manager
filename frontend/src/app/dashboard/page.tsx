'use client';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useState, useEffect } from 'react';
import { dashboardService, DashboardStats, RecentProject, RecentActivity } from '@/lib/api/services/dashboard';
import Link from 'next/link';

// 통계 카드 데이터 타입
interface StatCard {
  label: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
}

export default function DashboardPage() {
  const [stats, setStats] = useState<StatCard[]>([]);
  const [recentProjects, setRecentProjects] = useState<RecentProject[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔄 대시보드 데이터 로딩 시작...');

      // 모든 대시보드 데이터를 병렬로 요청
      const [dashboardData] = await Promise.all([
        dashboardService.getDashboardData(),
      ]);

      // 통계 데이터를 UI 형태로 변환
      const transformedStats: StatCard[] = [
        {
          label: '총 프로젝트',
          value: dashboardData.stats.total_projects.toString(),
          change: '+0', // 변화량은 백엔드에서 계산해서 제공해야 함
          changeType: 'neutral'
        },
        {
          label: '완료된 프로젝트',
          value: dashboardData.stats.completed_projects.toString(),
          change: '+0',
          changeType: 'positive'
        },
        {
          label: '진행 중',
          value: dashboardData.stats.active_projects.toString(),
          change: '+0',
          changeType: 'positive'
        },
        {
          label: '대기 중',
          value: dashboardData.stats.pending_projects.toString(),
          change: '+0',
          changeType: 'neutral'
        },
      ];

      setStats(transformedStats);
      setRecentProjects(dashboardData.recent_projects);
      setRecentActivities(dashboardData.recent_activities);

      console.log('✅ 대시보드 데이터 로딩 완료:', {
        stats: transformedStats,
        projects: dashboardData.recent_projects.length,
        activities: dashboardData.recent_activities.length
      });

    } catch (error) {
      console.error('❌ 대시보드 데이터 로딩 실패:', error);
      setError('대시보드 데이터를 불러올 수 없습니다.');
      
      // 개발 환경에서만 상세 에러 표시
      if (process.env.NODE_ENV === 'development') {
        console.error('에러 상세:', {
          name: error?.name,
          message: error?.message,
          status: error?.status,
          code: error?.code
        });
      }
    } finally {
      setLoading(false);
    }
  };

  // 상태 라벨 변환 함수
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return '진행 중';
      case 'completed': return '완료';
      case 'pending': return '대기 중';
      case 'archived': return '보관됨';
      default: return status;
    }
  };

  // 상태 색상 함수
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 활동 타입 라벨 변환 함수
  const getActivityLabel = (type: string, title: string, projectTitle?: string) => {
    switch (type) {
      case 'project_created':
        return `새로운 프로젝트 ${title}이 생성되었습니다`;
      case 'project_updated':
        return `${title} 프로젝트가 업데이트되었습니다`;
      case 'project_completed':
        return `${title} 프로젝트가 완료되었습니다`;
      case 'note_created':
        return `${projectTitle}에 새로운 노트가 작성되었습니다`;
      default:
        return title;
    }
  };

  // 활동 아이콘 색상
  const getActivityColor = (type: string) => {
    switch (type) {
      case 'project_created': return 'bg-blue-500';
      case 'project_updated': return 'bg-yellow-500';
      case 'project_completed': return 'bg-green-500';
      case 'note_created': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  // 시간 포맷 함수
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInHours < 1) {
      return '방금 전';
    } else if (diffInHours < 24) {
      return `${diffInHours}시간 전`;
    } else if (diffInDays < 7) {
      return `${diffInDays}일 전`;
    } else {
      return date.toLocaleDateString('ko-KR');
    }
  };

  // 로딩 상태
  if (loading) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <Header />
            <main className="flex-1 overflow-auto p-6">
              <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-center h-64">
                  <div className="text-gray-500">대시보드 데이터를 불러오는 중...</div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <Header />
            <main className="flex-1 overflow-auto p-6">
              <div className="max-w-7xl mx-auto">
                <div className="flex flex-col items-center justify-center h-64">
                  <div className="text-red-500 mb-4">{error}</div>
                  <button 
                    onClick={fetchDashboardData}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    다시 시도
                  </button>
                </div>
              </div>
            </main>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        {/* 사이드바 */}
        <Sidebar />

        {/* 메인 콘텐츠 영역 */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* 헤더 */}
          <Header />

          {/* 메인 콘텐츠 */}
          <main className="flex-1 overflow-auto p-4 md:p-6 pt-16 md:pt-6">
            <div className="max-w-7xl mx-auto">
              {/* 페이지 제목 */}
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
                <p className="text-gray-600 mt-2">
                  프로젝트 현황과 최근 활동을 확인하세요
                </p>
              </div>

              {/* 통계 카드 */}
              <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6 mb-8">
                {stats.map((stat, index) => (
                  <Card key={index}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 p-3 md:p-6">
                      <CardTitle className="text-xs md:text-sm font-medium truncate">
                        {stat.label}
                      </CardTitle>
                      <Badge
                        variant={
                          stat.changeType === 'positive'
                            ? 'default'
                            : stat.changeType === 'negative'
                              ? 'destructive'
                              : 'secondary'
                        }
                        className="text-xs hidden md:inline-flex"
                      >
                        {stat.change}
                      </Badge>
                    </CardHeader>
                    <CardContent className="p-3 md:p-6 pt-0">
                      <div className="text-lg md:text-2xl font-bold">{stat.value}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 최근 프로젝트 및 활동 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
                {/* 최근 프로젝트 */}
                <Card>
                  <CardHeader>
                    <CardTitle>최근 프로젝트</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recentProjects.length === 0 ? (
                        <div className="text-center text-gray-500 py-8">
                          최근 프로젝트가 없습니다
                        </div>
                      ) : (
                        recentProjects.map((project) => (
                          <div
                            key={project.id}
                            className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex-1">
                              <h3 className="font-medium text-gray-900">
                                <Link 
                                  href={`/projects/${project.id}`}
                                  className="hover:text-blue-600"
                                >
                                  {project.title}
                                </Link>
                              </h3>
                              <p className="text-sm text-gray-600 mt-1">
                                {project.description}
                              </p>
                              <div className="flex items-center mt-2 space-x-4">
                                <Badge
                                  className={getStatusColor(project.status)}
                                >
                                  {getStatusLabel(project.status)}
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  {formatRelativeTime(project.updated_at)}
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm font-medium text-gray-900">
                                조회 {project.view_count}
                              </div>
                              <div className="text-sm text-gray-500">
                                좋아요 {project.like_count}
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* 최근 활동 */}
                <Card>
                  <CardHeader>
                    <CardTitle>최근 활동</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recentActivities.length === 0 ? (
                        <div className="text-center text-gray-500 py-8">
                          최근 활동이 없습니다
                        </div>
                      ) : (
                        recentActivities.map((activity) => (
                          <div key={activity.id} className="flex items-start space-x-3">
                            <div className={`w-2 h-2 ${getActivityColor(activity.type)} rounded-full mt-2`}></div>
                            <div className="flex-1">
                              <p className="text-sm text-gray-900">
                                {getActivityLabel(activity.type, activity.title, activity.project_title)}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">
                                {formatRelativeTime(activity.created_at)}
                              </p>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}