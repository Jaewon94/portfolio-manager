import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  // 임시 데이터
  const stats = [
    { label: '총 프로젝트', value: '12', change: '+2', changeType: 'positive' },
    {
      label: '완료된 프로젝트',
      value: '8',
      change: '+1',
      changeType: 'positive',
    },
    { label: '진행 중', value: '3', change: '+1', changeType: 'positive' },
    { label: '대기 중', value: '1', change: '0', changeType: 'neutral' },
  ];

  const recentProjects = [
    {
      id: 1,
      title: '포트폴리오 매니저',
      description: 'AI 시대의 프로젝트 관리 대중화',
      status: '진행 중',
      progress: 75,
      lastUpdated: '2시간 전',
    },
    {
      id: 2,
      title: 'E-커머스 플랫폼',
      description: '온라인 쇼핑몰 구축 프로젝트',
      status: '완료',
      progress: 100,
      lastUpdated: '1일 전',
    },
    {
      id: 3,
      title: '모바일 앱 개발',
      description: 'React Native 기반 모바일 애플리케이션',
      status: '진행 중',
      progress: 45,
      lastUpdated: '3일 전',
    },
  ];

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        {/* 사이드바 */}
        <Sidebar />

        {/* 메인 콘텐츠 영역 */}
        <div className="flex-1 flex flex-col">
          {/* 헤더 */}
          <Header />

          {/* 메인 콘텐츠 */}
          <main className="flex-1 overflow-auto p-6">
            <div className="max-w-7xl mx-auto">
              {/* 페이지 제목 */}
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
                <p className="text-gray-600 mt-2">
                  프로젝트 현황과 최근 활동을 확인하세요
                </p>
              </div>

              {/* 통계 카드 */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {stats.map((stat, index) => (
                  <Card key={index}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">
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
                        className="text-xs"
                      >
                        {stat.change}
                      </Badge>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stat.value}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 최근 프로젝트 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>최근 프로젝트</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recentProjects.map((project) => (
                        <div
                          key={project.id}
                          className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">
                              {project.title}
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">
                              {project.description}
                            </p>
                            <div className="flex items-center mt-2 space-x-4">
                              <Badge
                                variant={
                                  project.status === '완료'
                                    ? 'default'
                                    : project.status === '진행 중'
                                      ? 'secondary'
                                      : 'outline'
                                }
                                className="text-xs"
                              >
                                {project.status}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {project.lastUpdated}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium text-gray-900">
                              {project.progress}%
                            </div>
                            <div className="w-16 h-2 bg-gray-200 rounded-full mt-1">
                              <div
                                className="h-2 bg-blue-600 rounded-full"
                                style={{ width: `${project.progress}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>최근 활동</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                          <p className="text-sm text-gray-900">
                            <span className="font-medium">
                              포트폴리오 매니저
                            </span>{' '}
                            프로젝트가 업데이트되었습니다
                          </p>
                          <p className="text-xs text-gray-500 mt-1">2시간 전</p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                          <p className="text-sm text-gray-900">
                            <span className="font-medium">E-커머스 플랫폼</span>{' '}
                            프로젝트가 완료되었습니다
                          </p>
                          <p className="text-xs text-gray-500 mt-1">1일 전</p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                          <p className="text-sm text-gray-900">
                            새로운 프로젝트{' '}
                            <span className="font-medium">모바일 앱 개발</span>
                            이 생성되었습니다
                          </p>
                          <p className="text-xs text-gray-500 mt-1">3일 전</p>
                        </div>
                      </div>
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
