import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  ExternalLink,
  FolderOpen,
  Github,
  Plus,
  StickyNote,
  TrendingUp,
  Users,
} from 'lucide-react';

export default function Home() {
  // 임시 데이터 (나중에 API에서 가져올 예정)
  const stats = [
    { title: '총 프로젝트', value: '12', icon: FolderOpen, trend: '+2' },
    { title: '총 노트', value: '48', icon: StickyNote, trend: '+5' },
    { title: '이번 주 방문자', value: '156', icon: Users, trend: '+12%' },
    { title: '완성도 점수', value: '85', icon: TrendingUp, trend: '+3' },
  ];

  const recentProjects = [
    {
      id: 1,
      title: 'React 포트폴리오',
      description: 'Next.js와 TypeScript로 만든 포트폴리오 웹사이트',
      tech: ['React', 'TypeScript', 'Tailwind'],
      status: '완료',
      url: 'https://example.com',
      github: 'https://github.com/example/portfolio',
    },
    {
      id: 2,
      title: 'Python ML 프로젝트',
      description: '머신러닝을 활용한 데이터 분석 프로젝트',
      tech: ['Python', 'TensorFlow', 'Pandas'],
      status: '개발중',
      url: 'https://example.com',
      github: 'https://github.com/example/ml-project',
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* 환영 메시지 */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">안녕하세요! 👋</h1>
        <p className="text-muted-foreground">
          오늘도 멋진 포트폴리오를 만들어보세요.
        </p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">{stat.trend}</span> 지난 주
                대비
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 최근 프로젝트 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">최근 프로젝트</h2>
          <Button>
            <Plus className="h-4 w-4 mr-2" />새 프로젝트
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentProjects.map((project) => (
            <Card
              key={project.id}
              className="hover:shadow-md transition-shadow"
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{project.title}</CardTitle>
                  <Badge
                    variant={
                      project.status === '완료' ? 'default' : 'secondary'
                    }
                  >
                    {project.status}
                  </Badge>
                </div>
                <CardDescription>{project.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-1">
                  {project.tech.map((tech) => (
                    <Badge key={tech} variant="outline" className="text-xs">
                      {tech}
                    </Badge>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <ExternalLink className="h-3 w-3 mr-1" />
                    데모
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Github className="h-3 w-3 mr-1" />
                    코드
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* 빠른 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>빠른 액션</CardTitle>
          <CardDescription>
            자주 사용하는 기능에 빠르게 접근하세요.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex-col">
              <FolderOpen className="h-6 w-6 mb-2" />새 프로젝트
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <StickyNote className="h-6 w-6 mb-2" />새 노트
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Github className="h-6 w-6 mb-2" />
              GitHub 연동
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <TrendingUp className="h-6 w-6 mb-2" />
              통계 보기
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
