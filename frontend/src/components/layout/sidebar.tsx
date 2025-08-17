"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
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
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div
      className={cn(
        "flex flex-col bg-card border-r transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* 사이드바 헤더 */}
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <h1 className="text-xl font-bold text-primary">Portfolio</h1>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="ml-auto"
        >
          {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
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
                  collapsed && "justify-center px-2"
                )}
              >
                <item.icon className="h-4 w-4 mr-2" />
                {!collapsed && item.name}
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
              collapsed && "justify-center px-2"
            )}
          >
            <Settings className="h-4 w-4 mr-2" />
            {!collapsed && "설정"}
          </Button>
        </Link>
      </div>
    </div>
  );
}
