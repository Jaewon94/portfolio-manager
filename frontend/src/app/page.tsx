import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 헤더 */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">P</span>
              </div>
              <span className="text-xl font-bold text-gray-900">
                Portfolio Manager
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/login">
                <Button variant="ghost">로그인</Button>
              </Link>
              <Link href="/auth/register">
                <Button>회원가입</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* 히어로 섹션 */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI 시대의 프로젝트 관리
            <span className="text-blue-600 block">대중화</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI 도구로 만든 수많은 프로젝트들을 체계적으로 관리하고, 효과적으로
            소개할 수 있는 통합 포트폴리오 관리 플랫폼
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register">
              <Button size="lg" className="text-lg px-8 py-3">
                무료로 시작하기
              </Button>
            </Link>
            <Link href="/auth/login">
              <Button variant="outline" size="lg" className="text-lg px-8 py-3">
                이미 계정이 있나요?
              </Button>
            </Link>
          </div>
        </div>

        {/* 주요 기능 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <CardTitle>AI 프로젝트 통합 관리</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                GitHub, Vercel, Replit 등에 흩어진 프로젝트들을 한 곳에서
                체계적으로 관리하고 AI 프롬프트와 학습 과정까지 함께 기록
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <CardTitle>효과적인 포트폴리오</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                기술적 내용을 스토리로 설명하고, 프로젝트 제작 과정을 투명하게
                보여주어 채용담당자와 클라이언트에게 전문성을 어필
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  />
                </svg>
              </div>
              <CardTitle>지식 관리 시스템</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                AI와의 대화 내용, 프롬프트, 학습 과정을 체계적으로 저장하여
                개인의 성장 과정을 추적하고 증명
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* 사용자 시나리오 */}
        <div className="bg-white rounded-2xl p-8 mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">
            누구를 위한 서비스인가요?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">
                🤖 AI 네이티브 창작자
              </h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Claude, GPT, Cursor로 프로젝트를 만드는 분</li>
                <li>• 코딩 부트캠프 수강생</li>
                <li>• 사이드 프로젝트를 시작한 직장인</li>
                <li>• 포트폴리오가 필요한 대학생</li>
              </ul>
            </div>
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">
                💻 기존 개발자
              </h3>
              <ul className="space-y-2 text-gray-600">
                <li>• AI 도구로 생산성이 높아진 개발자</li>
                <li>• 여러 실험적 프로젝트를 진행하는 창작자</li>
                <li>• 포트폴리오 차별화가 필요한 개발자</li>
                <li>• 지식 관리를 체계화하고 싶은 분</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA 섹션 */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            지금 시작해서 AI 시대의 포트폴리오를 만들어보세요
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            무료로 가입하고 첫 프로젝트를 등록해보세요
          </p>
          <Link href="/auth/register">
            <Button size="lg" className="text-lg px-8 py-3">
              무료로 시작하기
            </Button>
          </Link>
        </div>
      </main>

      {/* 푸터 */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">P</span>
              </div>
              <span className="text-xl font-bold">Portfolio Manager</span>
            </div>
            <p className="text-gray-400">AI 시대의 프로젝트 관리 대중화</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
