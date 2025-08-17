'use client';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { noteService } from '@/lib/api/services/notes';
import { projectService } from '@/lib/api/services/projects';
import { Note, NoteType, Project } from '@/types/api';
import {
  Archive,
  BookOpen,
  Calendar,
  FileText,
  GitBranch,
  Microscope,
  MoreVertical,
  Pin,
  Plus,
  Search,
  Tag,
} from 'lucide-react';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'learn' | 'change' | 'research'>(
    'learn'
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  const fetchProjects = useCallback(async () => {
    try {
      setProjectsLoading(true);
      console.log('🔄 프로젝트 목록 조회 시작...');

      const response = await projectService.getProjects({
        page: 1,
        page_size: 100,
      });

      console.log('✅ 프로젝트 목록 조회 완료:', response);
      const projectList = response.projects || [];
      setProjects(projectList);

      // 첫 번째 프로젝트를 기본 선택
      if (projectList.length > 0 && !selectedProject) {
        setSelectedProject(projectList[0].id);
      }
    } catch (error) {
      console.error('❌ 프로젝트 목록 조회 실패:', error);
    } finally {
      setProjectsLoading(false);
    }
  }, [selectedProject]);

  const fetchNotes = useCallback(async () => {
    try {
      setLoading(true);
      console.log('🔄 노트 목록 요청 시작...');

      if (selectedProject) {
        // 특정 프로젝트의 노트 조회
        const response = await noteService.getNotesByType(
          selectedProject,
          activeTab as NoteType
        );
        console.log('✅ 노트 API 응답:', response);
        setNotes(response || []);
      } else {
        // 프로젝트가 선택되지 않은 경우 빈 배열
        console.log('⚠️ 프로젝트가 선택되지 않음');
        setNotes([]);
      }
    } catch (error) {
      console.error('❌ 노트 조회 실패:', error);

      // 개발 환경에서만 상세 에러 정보 표시
      if (process.env.NODE_ENV === 'development') {
        console.error('에러 상세:', {
          name: error instanceof Error ? error.name : 'Unknown',
          message: error instanceof Error ? error.message : String(error),
          status:
            'status' in (error as object)
              ? (error as { status: unknown }).status
              : undefined,
          code:
            'code' in (error as object)
              ? (error as { code: unknown }).code
              : undefined,
        });
      }

      // 실제 빈 상태 표시 (더미 데이터 제거)
      setNotes([]);
    } finally {
      setLoading(false);
    }
  }, [selectedProject, activeTab]);

  // useEffect hooks
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const filteredNotes = notes.filter((note) => {
    const matchesSearch =
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.tags?.some((tag) =>
        tag.toLowerCase().includes(searchQuery.toLowerCase())
      );
    return matchesSearch && !note.is_archived;
  });

  const getTabIcon = (type: string) => {
    switch (type) {
      case 'learn':
        return <BookOpen className="w-4 h-4" />;
      case 'change':
        return <GitBranch className="w-4 h-4" />;
      case 'research':
        return <Microscope className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getTabLabel = (type: string) => {
    switch (type) {
      case 'learn':
        return '학습';
      case 'change':
        return '변경';
      case 'research':
        return '조사';
      default:
        return type;
    }
  };

  const getTabDescription = (type: string) => {
    switch (type) {
      case 'learn':
        return '새로운 기술과 개념을 학습한 내용을 기록하세요';
      case 'change':
        return '프로젝트의 변경사항과 업데이트를 추적하세요';
      case 'research':
        return '기술 조사와 리서치 결과를 정리하세요';
      default:
        return '';
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
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">노트</h1>
                  <p className="text-gray-600 mt-2">
                    프로젝트 진행 과정과 학습 내용을 체계적으로 기록하세요
                  </p>
                </div>
                <Button className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />새 노트
                </Button>
              </div>

              {/* 프로젝트 선택 및 검색 바 */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                {/* 프로젝트 선택 */}
                <div className="sm:w-64">
                  <select
                    className="w-full px-4 py-2 border rounded-lg text-sm"
                    value={selectedProject || ''}
                    onChange={(e) =>
                      setSelectedProject(
                        e.target.value ? Number(e.target.value) : null
                      )
                    }
                    disabled={projectsLoading}
                  >
                    <option value="">프로젝트 선택</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.title}
                      </option>
                    ))}
                  </select>
                </div>

                {/* 검색 바 */}
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="노트 검색... (제목, 태그)"
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>

              {/* 탭 네비게이션 */}
              <Tabs
                value={activeTab}
                onValueChange={(value) =>
                  setActiveTab(value as 'learn' | 'change' | 'research')
                }
              >
                <TabsList className="grid grid-cols-3 w-full mb-6">
                  <TabsTrigger
                    value="learn"
                    className="flex items-center gap-2"
                  >
                    {getTabIcon('learn')}
                    {getTabLabel('learn')}
                  </TabsTrigger>
                  <TabsTrigger
                    value="change"
                    className="flex items-center gap-2"
                  >
                    {getTabIcon('change')}
                    {getTabLabel('change')}
                  </TabsTrigger>
                  <TabsTrigger
                    value="research"
                    className="flex items-center gap-2"
                  >
                    {getTabIcon('research')}
                    {getTabLabel('research')}
                  </TabsTrigger>
                </TabsList>

                {/* 탭 설명 */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-start gap-2">
                    {getTabIcon(activeTab)}
                    <div>
                      <h3 className="font-medium text-blue-900">
                        {getTabLabel(activeTab)} 노트
                      </h3>
                      <p className="text-sm text-blue-700 mt-1">
                        {getTabDescription(activeTab)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 노트 목록 */}
                {['learn', 'change', 'research'].map((tabType) => (
                  <TabsContent key={tabType} value={tabType}>
                    {loading || projectsLoading ? (
                      <div className="flex items-center justify-center h-64">
                        <div className="text-gray-500">
                          {projectsLoading
                            ? '프로젝트를 불러오는 중...'
                            : '노트를 불러오는 중...'}
                        </div>
                      </div>
                    ) : !selectedProject ? (
                      <div className="flex flex-col items-center justify-center h-64">
                        <div className="text-gray-500 mb-4">
                          프로젝트를 선택해주세요
                        </div>
                        {projects.length === 0 && (
                          <Link href="/projects/new">
                            <Button>첫 프로젝트 만들기</Button>
                          </Link>
                        )}
                      </div>
                    ) : filteredNotes.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-64">
                        <div className="text-gray-500 mb-4">
                          {searchQuery
                            ? '검색 결과가 없습니다'
                            : `${getTabLabel(tabType)} 노트가 없습니다`}
                        </div>
                        <Button>첫 노트 작성하기</Button>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredNotes.map((note) => (
                          <Card
                            key={note.id}
                            className="hover:shadow-lg transition-shadow cursor-pointer relative"
                          >
                            {note.is_pinned && (
                              <div className="absolute top-4 right-4">
                                <Pin className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                              </div>
                            )}
                            <CardHeader>
                              <CardTitle className="text-lg pr-8">
                                {note.title}
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                {/* 내용 미리보기 */}
                                <p className="text-sm text-gray-600 line-clamp-3">
                                  {typeof note.content === 'object' &&
                                  note.content &&
                                  'text' in note.content
                                    ? String(note.content.text)
                                    : '내용 없음'}
                                </p>

                                {/* 태그 */}
                                {note.tags && note.tags.length > 0 && (
                                  <div className="flex flex-wrap gap-1">
                                    {note.tags.slice(0, 3).map((tag) => (
                                      <Badge
                                        key={tag}
                                        variant="secondary"
                                        className="text-xs"
                                      >
                                        <Tag className="w-3 h-3 mr-1" />
                                        {tag}
                                      </Badge>
                                    ))}
                                    {note.tags.length > 3 && (
                                      <Badge
                                        variant="secondary"
                                        className="text-xs"
                                      >
                                        +{note.tags.length - 3}
                                      </Badge>
                                    )}
                                  </div>
                                )}

                                {/* 메타 정보 */}
                                <div className="flex items-center gap-3 text-xs text-gray-500">
                                  <div className="flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    {new Date(
                                      note.updated_at
                                    ).toLocaleDateString('ko-KR')}
                                  </div>
                                </div>

                                {/* 액션 버튼 */}
                                <div className="flex gap-2 pt-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="flex-1"
                                  >
                                    편집
                                  </Button>
                                  <Button variant="ghost" size="sm">
                                    <Archive className="w-4 h-4" />
                                  </Button>
                                  <Button variant="ghost" size="sm">
                                    <MoreVertical className="w-4 h-4" />
                                  </Button>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </TabsContent>
                ))}
              </Tabs>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
