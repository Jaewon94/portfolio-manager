'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { useAuthStore } from '@/stores/authStore';
import { useSidebarStore } from '@/stores/sidebarStore';
import { Bell, LogOut, Search, Settings, User, Menu } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isMobile, setIsMobile] = useState(false);
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { toggleMobile } = useSidebarStore();

  // 모바일 화면 감지
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // 검색 로직 구현
    console.log('Search:', searchQuery);
  };

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  return (
    <header className="flex items-center justify-between p-3 md:p-4 border-b bg-background sticky top-0 z-50">
      {/* 모바일 메뉴 버튼 */}
      {isMobile && (
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={toggleMobile}
          className="mr-2 md:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
      )}

      {/* 검색바 */}
      <div className="flex-1 max-w-xs sm:max-w-md lg:max-w-2xl">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            type="text"
            placeholder={isMobile ? "검색..." : "프로젝트, 노트, 사용자 검색..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-4 text-sm"
          />
        </form>
      </div>

      {/* 우측 메뉴 */}
      <div className="flex items-center space-x-2 md:space-x-4 ml-2 md:ml-4">
        {/* 알림 - 데스크톱에서만 표시 */}
        <Button variant="ghost" size="sm" className="hidden sm:flex">
          <Bell className="h-4 w-4" />
        </Button>

        {/* 사용자 프로필 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarImage
                  src={user?.avatar_url || '/avatars/default.png'}
                  alt="User"
                />
                <AvatarFallback className="text-xs">
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-48 sm:w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none truncate">
                  {user?.name || '사용자'}
                </p>
                <p className="text-xs leading-none text-muted-foreground truncate">
                  {user?.email || 'user@example.com'}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>프로필</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>설정</span>
            </DropdownMenuItem>
            {/* 모바일에서는 알림도 메뉴에 포함 */}
            <DropdownMenuItem className="sm:hidden">
              <Bell className="mr-2 h-4 w-4" />
              <span>알림</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              <span>로그아웃</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
