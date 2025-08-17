'use client';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  Plus, 
  Grid3X3, 
  List, 
  MoreVertical,
  Star,
  Eye,
  Calendar,
  ExternalLink
} from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { projectService } from '@/lib/api/services/projects';
import { Project, ProjectStatus, ProjectVisibility } from '@/types/api';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      console.log('🔄 프로젝트 목록 요청 시작...');
      
      const response = await projectService.getProjects({
        page: 1,
        page_size: 20,
      });
      
      console.log('✅ 프로젝트 API 응답:', response);
      setProjects(response.projects || []);
    } catch (error) {
      console.error('❌ 프로젝트 조회 실패:', error);
      
      // 개발 환경에서만 상세 에러 정보 표시
      if (process.env.NODE_ENV === 'development') {
        console.error('에러 상세:', {
          name: error instanceof Error ? error.name : 'Unknown',
          message: error instanceof Error ? error.message : String(error),
          status: 'status' in (error as object) ? (error as { status: unknown }).status : undefined,
          code: 'code' in (error as object) ? (error as { code: unknown }).code : undefined
        });
      }
      
      // 실제 빈 상태 표시 (더미 데이터 제거)
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          project.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || project.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.DRAFT: return 'bg-yellow-100 text-yellow-800';
      case ProjectStatus.PUBLISHED: return 'bg-green-100 text-green-800';
      case ProjectStatus.ARCHIVED: return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusLabel = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.DRAFT: return '초안';
      case ProjectStatus.PUBLISHED: return '발행됨';
      case ProjectStatus.ARCHIVED: return '보관됨';
      default: return '알 수 없음';
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        
        <div className="flex-1 flex flex-col min-w-0">
          <Header />
          
          <main className="flex-1 overflow-auto p-4 md:p-6 pt-16 md:pt-6">
            <div className="max-w-7xl mx-auto">
              {/* 페이지 헤더 */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 md:mb-8 gap-4">
                <div>
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900">프로젝트</h1>
                  <p className="text-gray-600 mt-1 md:mt-2 text-sm md:text-base">
                    모든 프로젝트를 한 곳에서 관리하세요
                  </p>
                </div>
                <Link href="/projects/new">
                  <Button className="flex items-center gap-2 w-full sm:w-auto">
                    <Plus className="w-4 h-4" />
                    <span className="sm:inline">새 프로젝트</span>
                  </Button>
                </Link>
              </div>

              {/* 검색 및 필터 바 */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="프로젝트 검색..."
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                
                <div className="flex flex-col sm:flex-row gap-2">
                  <div className="relative w-full sm:w-auto min-w-[120px]">
                    <select
                      className="px-4 py-2 pr-8 border rounded-lg text-sm w-full appearance-none bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                    >
                      <option value="all">모든 상태</option>
                      <option value={ProjectStatus.DRAFT}>초안</option>
                      <option value={ProjectStatus.PUBLISHED}>발행됨</option>
                      <option value={ProjectStatus.ARCHIVED}>보관됨</option>
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                  
                  <div className="flex border rounded-lg w-full sm:w-auto">
                    <Button
                      variant={viewMode === 'grid' ? 'default' : 'ghost'}
                      size="sm"
                      className="px-3 flex-1 sm:flex-none"
                      onClick={() => setViewMode('grid')}
                    >
                      <Grid3X3 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant={viewMode === 'list' ? 'default' : 'ghost'}
                      size="sm"
                      className="px-3 flex-1 sm:flex-none"
                      onClick={() => setViewMode('list')}
                    >
                      <List className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* 프로젝트 목록 */}
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-gray-500">프로젝트를 불러오는 중...</div>
                </div>
              ) : filteredProjects.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64">
                  <div className="text-gray-500 mb-4">프로젝트가 없습니다</div>
                  <Link href="/projects/new">
                    <Button>첫 프로젝트 만들기</Button>
                  </Link>
                </div>
              ) : (
                <div className={viewMode === 'grid' 
                  ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6' 
                  : 'space-y-4'
                }>
                  {filteredProjects.map((project) => (
                    <Card 
                      key={project.id} 
                      className="hover:shadow-lg transition-shadow cursor-pointer"
                    >
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              {project.featured && (
                                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                              )}
                              <Badge className={getStatusColor(project.status)}>
                                {getStatusLabel(project.status)}
                              </Badge>
                              <Badge variant={project.visibility === ProjectVisibility.PUBLIC ? 'outline' : 'secondary'}>
                                {project.visibility === ProjectVisibility.PUBLIC ? '공개' : '비공개'}
                              </Badge>
                            </div>
                            <CardTitle className="text-lg">
                              <Link href={`/projects/${project.id}`} className="hover:text-blue-600">
                                {project.title}
                              </Link>
                            </CardTitle>
                            <CardDescription className="mt-2 line-clamp-2">
                              {project.description}
                            </CardDescription>
                          </div>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {/* 기술 스택 */}
                          <div className="flex flex-wrap gap-1">
                            {project.tech_stack?.slice(0, 3).map((tech) => (
                              <Badge key={tech} variant="secondary" className="text-xs">
                                {tech}
                              </Badge>
                            ))}
                            {project.tech_stack && project.tech_stack.length > 3 && (
                              <Badge variant="secondary" className="text-xs">
                                +{project.tech_stack.length - 3}
                              </Badge>
                            )}
                          </div>
                          
                          {/* 통계 */}
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <div className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              <span>{project.view_count}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Star className="w-3 h-3" />
                              <span>{project.like_count}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              <span>{new Date(project.updated_at).toLocaleDateString('ko-KR')}</span>
                            </div>
                          </div>
                          
                          {/* 액션 버튼 */}
                          <div className="flex gap-2 pt-2">
                            <Link href={`/projects/${project.id}/edit`} className="flex-1">
                              <Button variant="outline" size="sm" className="w-full">
                                편집
                              </Button>
                            </Link>
                            {project.visibility === ProjectVisibility.PUBLIC && (
                              <Button variant="outline" size="sm">
                                <ExternalLink className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}