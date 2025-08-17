"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useSidebarStore } from "@/stores/sidebarStore";
import {
  LayoutDashboard,
  FolderOpen,
  StickyNote,
  Search,
  Settings,
  Menu,
  X,
} from "lucide-react";

const navigation = [
  {
    name: "대시보드",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "프로젝트",
    href: "/projects",
    icon: FolderOpen,
  },
  {
    name: "노트",
    href: "/notes",
    icon: StickyNote,
  },
  {
    name: "검색",
    href: "/search",
    icon: Search,
  },
];

export function Sidebar() {
  const [isMobile, setIsMobile] = useState(false);
  const pathname = usePathname();
  const { mobileOpen, collapsed, toggleMobile, closeMobile, toggleCollapsed } = useSidebarStore();

  // 모바일 화면 감지
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        closeMobile();
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, [closeMobile]);

  // 모바일에서 경로 변경 시 사이드바 닫기
  useEffect(() => {
    if (isMobile) {
      closeMobile();
    }
  }, [pathname, isMobile, closeMobile]);

  // 모바일 오버레이 클릭 시 사이드바 닫기
  const handleOverlayClick = () => {
    closeMobile();
  };

  return (
    <>
      {/* 모바일 오버레이 */}
      {isMobile && mobileOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={handleOverlayClick}
        />
      )}

      {/* 모바일 메뉴 버튼 - Header에서 제어하므로 제거 */}
      <div
        className={cn(
          "flex flex-col bg-card border-r transition-all duration-300",
          // 데스크톱: 기존 접기/펼치기 동작
          !isMobile && (collapsed ? "w-16" : "w-64"),
          // 모바일: 전체 화면 오버레이 또는 숨김
          isMobile && (
            mobileOpen 
              ? "fixed left-0 top-0 h-full w-64 z-50" 
              : "hidden"
          )
        )}
      >
        {/* 사이드바 헤더 */}
        <div className="flex items-center justify-between p-4 border-b">
          {(!collapsed || isMobile) && (
            <h1 className="text-xl font-bold text-primary">Portfolio</h1>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              if (isMobile) {
                toggleMobile();
              } else {
                toggleCollapsed();
              }
            }}
            className="ml-auto"
          >
            {isMobile ? (
              <X className="h-4 w-4" />
            ) : (
              collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* 네비게이션 메뉴 */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.name} href={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start",
                    !isMobile && collapsed && "justify-center px-2"
                  )}
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {(!collapsed || isMobile) && item.name}
                </Button>
              </Link>
            );
          })}
        </nav>

        <Separator />

        {/* 하단 메뉴 */}
        <div className="p-4">
          <Link href="/settings">
            <Button
              variant="ghost"
              className={cn(
                "w-full justify-start",
                !isMobile && collapsed && "justify-center px-2"
              )}
            >
              <Settings className="h-4 w-4 mr-2" />
              {(!collapsed || isMobile) && "설정"}
            </Button>
          </Link>
        </div>
      </div>
    </>
  );
}
