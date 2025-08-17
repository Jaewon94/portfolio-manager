'use client';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft,
  Save,
  Plus,
  X,
  Globe,
  Lock,
  Star
} from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { projectService } from '@/lib/api/services/projects';

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    description: '',
    status: 'active',
    visibility: 'public',
    featured: false,
    tech_stack: [] as string[],
    categories: [] as string[],
    tags: [] as string[],
    github_url: '',
  });
  
  const [techInput, setTechInput] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [categoryInput, setCategoryInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // API 호출
      await projectService.createProject({
        ...formData,
        content: {},
      });
      
      // 성공 시 프로젝트 목록으로 이동
      router.push('/projects');
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('프로젝트 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTech = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && techInput.trim()) {
      e.preventDefault();
      setFormData({
        ...formData,
        tech_stack: [...formData.tech_stack, techInput.trim()]
      });
      setTechInput('');
    }
  };

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const handleAddCategory = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && categoryInput.trim()) {
      e.preventDefault();
      setFormData({
        ...formData,
        categories: [...formData.categories, categoryInput.trim()]
      });
      setCategoryInput('');
    }
  };

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9가-힣]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        
        <div className="flex-1 flex flex-col">
          <Header />
          
          <main className="flex-1 overflow-auto p-4 md:p-6 pt-16 md:pt-6">
            <div className="max-w-4xl mx-auto">
              {/* 페이지 헤더 */}
              <div className="flex items-start gap-3 md:gap-4 mb-6 md:mb-8">
                <Link href="/projects">
                  <Button variant="ghost" size="sm" className="mt-1">
                    <ArrowLeft className="w-4 h-4" />
                  </Button>
                </Link>
                <div className="flex-1">
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900">새 프로젝트</h1>
                  <p className="text-gray-600 mt-1 text-sm md:text-base">
                    프로젝트 정보를 입력하여 포트폴리오에 추가하세요
                  </p>
                </div>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="space-y-4 md:space-y-6">
                  {/* 기본 정보 */}
                  <Card>
                    <CardHeader className="p-4 md:p-6">
                      <CardTitle className="text-lg md:text-xl">기본 정보</CardTitle>
                      <CardDescription className="text-sm md:text-base">
                        프로젝트의 기본 정보를 입력하세요
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4 p-4 md:p-6 pt-0">
                      <div>
                        <Label htmlFor="title">프로젝트 이름 *</Label>
                        <Input
                          id="title"
                          value={formData.title}
                          onChange={(e) => {
                            setFormData({
                              ...formData,
                              title: e.target.value,
                              slug: generateSlug(e.target.value)
                            });
                          }}
                          placeholder="예: 포트폴리오 매니저"
                          required
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="slug">URL 슬러그</Label>
                        <Input
                          id="slug"
                          value={formData.slug}
                          onChange={(e) => setFormData({...formData, slug: e.target.value})}
                          placeholder="portfolio-manager"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          프로젝트 URL에 사용될 고유 식별자입니다
                        </p>
                      </div>
                      
                      <div>
                        <Label htmlFor="description">설명</Label>
                        <textarea
                          id="description"
                          className="w-full min-h-[80px] md:min-h-[100px] px-3 py-2 border rounded-lg resize-none text-sm md:text-base"
                          value={formData.description}
                          onChange={(e) => setFormData({...formData, description: e.target.value})}
                          placeholder="프로젝트에 대한 간단한 설명을 작성하세요"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="github">GitHub URL</Label>
                        <Input
                          id="github"
                          type="url"
                          value={formData.github_url}
                          onChange={(e) => setFormData({...formData, github_url: e.target.value})}
                          placeholder="https://github.com/username/repository"
                        />
                      </div>
                    </CardContent>
                  </Card>

                  {/* 기술 스택 */}
                  <Card>
                    <CardHeader className="p-4 md:p-6">
                      <CardTitle className="text-lg md:text-xl">기술 스택</CardTitle>
                      <CardDescription className="text-sm md:text-base">
                        프로젝트에 사용된 기술들을 추가하세요
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-4 md:p-6 pt-0">
                      <div>
                        <Input
                          value={techInput}
                          onChange={(e) => setTechInput(e.target.value)}
                          onKeyDown={handleAddTech}
                          placeholder="기술 이름 입력 후 Enter (예: React, Node.js)"
                        />
                        <div className="flex flex-wrap gap-2 mt-3">
                          {formData.tech_stack.map((tech, index) => (
                            <Badge key={index} variant="secondary" className="px-3 py-1">
                              {tech}
                              <button
                                type="button"
                                onClick={() => {
                                  setFormData({
                                    ...formData,
                                    tech_stack: formData.tech_stack.filter((_, i) => i !== index)
                                  });
                                }}
                                className="ml-2"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 카테고리 & 태그 */}
                  <Card>
                    <CardHeader className="p-4 md:p-6">
                      <CardTitle className="text-lg md:text-xl">분류</CardTitle>
                      <CardDescription className="text-sm md:text-base">
                        프로젝트를 분류할 카테고리와 태그를 추가하세요
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4 p-4 md:p-6 pt-0">
                      <div>
                        <Label htmlFor="category" className="text-sm md:text-base">카테고리</Label>
                        <Input
                          id="category"
                          value={categoryInput}
                          onChange={(e) => setCategoryInput(e.target.value)}
                          onKeyDown={handleAddCategory}
                          placeholder="카테고리 입력 후 Enter (예: 웹개발, 모바일)"
                          className="text-sm md:text-base"
                        />
                        <div className="flex flex-wrap gap-2 mt-3">
                          {formData.categories.map((category, index) => (
                            <Badge key={index} variant="outline" className="px-2 md:px-3 py-1 text-xs md:text-sm">
                              {category}
                              <button
                                type="button"
                                onClick={() => {
                                  setFormData({
                                    ...formData,
                                    categories: formData.categories.filter((_, i) => i !== index)
                                  });
                                }}
                                className="ml-1 md:ml-2"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <Label htmlFor="tag" className="text-sm md:text-base">태그</Label>
                        <Input
                          id="tag"
                          value={tagInput}
                          onChange={(e) => setTagInput(e.target.value)}
                          onKeyDown={handleAddTag}
                          placeholder="태그 입력 후 Enter"
                          className="text-sm md:text-base"
                        />
                        <div className="flex flex-wrap gap-2 mt-3">
                          {formData.tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="px-2 md:px-3 py-1 text-xs md:text-sm">
                              #{tag}
                              <button
                                type="button"
                                onClick={() => {
                                  setFormData({
                                    ...formData,
                                    tags: formData.tags.filter((_, i) => i !== index)
                                  });
                                }}
                                className="ml-1 md:ml-2"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 설정 */}
                  <Card>
                    <CardHeader className="p-4 md:p-6">
                      <CardTitle className="text-lg md:text-xl">설정</CardTitle>
                      <CardDescription className="text-sm md:text-base">
                        프로젝트 공개 설정 및 상태를 선택하세요
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4 md:space-y-6 p-4 md:p-6 pt-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div className="flex-1">
                          <Label className="text-sm md:text-base">공개 설정</Label>
                          <p className="text-xs md:text-sm text-gray-500">프로젝트 공개 여부를 선택하세요</p>
                        </div>
                        <div className="flex gap-2 w-full sm:w-auto">
                          <Button
                            type="button"
                            variant={formData.visibility === 'public' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setFormData({...formData, visibility: 'public'})}
                            className="flex-1 sm:flex-none"
                          >
                            <Globe className="w-4 h-4 mr-1" />
                            <span className="text-xs md:text-sm">공개</span>
                          </Button>
                          <Button
                            type="button"
                            variant={formData.visibility === 'private' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setFormData({...formData, visibility: 'private'})}
                            className="flex-1 sm:flex-none"
                          >
                            <Lock className="w-4 h-4 mr-1" />
                            <span className="text-xs md:text-sm">비공개</span>
                          </Button>
                        </div>
                      </div>
                      
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div className="flex-1">
                          <Label className="text-sm md:text-base">프로젝트 상태</Label>
                          <p className="text-xs md:text-sm text-gray-500">현재 프로젝트 진행 상태</p>
                        </div>
                        <div className="relative w-full sm:w-auto min-w-[120px]">
                          <select
                            className="px-3 py-2 pr-8 border rounded-lg text-xs md:text-sm w-full appearance-none bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={formData.status}
                            onChange={(e) => setFormData({...formData, status: e.target.value})}
                          >
                            <option value="active">진행중</option>
                            <option value="completed">완료</option>
                            <option value="paused">일시중지</option>
                            <option value="archived">보관됨</option>
                          </select>
                          <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div className="flex-1">
                          <Label className="text-sm md:text-base">주요 프로젝트</Label>
                          <p className="text-xs md:text-sm text-gray-500">대표 프로젝트로 표시</p>
                        </div>
                        <Button
                          type="button"
                          variant={formData.featured ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setFormData({...formData, featured: !formData.featured})}
                          className="w-full sm:w-auto"
                        >
                          <Star className={`w-4 h-4 ${formData.featured ? 'fill-current' : ''} mr-1 sm:mr-0`} />
                          <span className="sm:hidden ml-1">{formData.featured ? '설정됨' : '설정'}</span>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 액션 버튼 */}
                  <div className="flex flex-col sm:flex-row justify-end gap-3">
                    <Link href="/projects" className="w-full sm:w-auto">
                      <Button variant="outline" className="w-full sm:w-auto">취소</Button>
                    </Link>
                    <Button type="submit" disabled={loading} className="w-full sm:w-auto">
                      <Save className="w-4 h-4 mr-2" />
                      <span className="text-sm md:text-base">{loading ? '저장 중...' : '프로젝트 생성'}</span>
                    </Button>
                  </div>
                </div>
              </form>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}