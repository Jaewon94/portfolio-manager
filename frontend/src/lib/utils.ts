import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 날짜 포맷팅 유틸리티
export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions) {
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  }).format(new Date(date))
}

export function formatRelativeTime(date: string | Date) {
  const now = new Date()
  const target = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - target.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return '방금 전'
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes}분 전`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours}시간 전`
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days}일 전`
  } else {
    return formatDate(date)
  }
}

// 슬러그 생성 유틸리티
export function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // 특수문자 제거
    .replace(/[\s_-]+/g, '-') // 공백과 밑줄을 하이픈으로
    .replace(/^-+|-+$/g, '') // 시작과 끝의 하이픈 제거
}

// 파일 크기 포맷팅
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 배열을 쉼표로 구분된 문자열로 변환
export function arrayToString(arr: string[]): string {
  return arr.join(', ')
}

// 쉼표로 구분된 문자열을 배열로 변환
export function stringToArray(str: string): string[] {
  return str.split(',').map(item => item.trim()).filter(item => item.length > 0)
}

// URL 유효성 검사
export function isValidUrl(string: string): boolean {
  try {
    new URL(string)
    return true
  } catch {
    return false
  }
}

// GitHub URL에서 저장소 이름 추출
export function extractGitHubRepo(url: string): string | null {
  const match = url.match(/github\.com\/([^\/]+\/[^\/]+)/)
  return match ? match[1] : null
}

// 색상 선택 (태그, 카테고리용)
export function getTagColor(tag: string): string {
  const colors = [
    'bg-blue-100 text-blue-800',
    'bg-green-100 text-green-800', 
    'bg-yellow-100 text-yellow-800',
    'bg-red-100 text-red-800',
    'bg-purple-100 text-purple-800',
    'bg-pink-100 text-pink-800',
    'bg-indigo-100 text-indigo-800',
    'bg-gray-100 text-gray-800',
  ]
  
  // 태그 이름의 해시값을 기반으로 색상 선택
  let hash = 0
  for (let i = 0; i < tag.length; i++) {
    hash = ((hash << 5) - hash + tag.charCodeAt(i)) & 0xffffffff
  }
  return colors[Math.abs(hash) % colors.length]
}

// 노트 타입에 따른 아이콘과 색상
export function getNoteTypeConfig(type: 'learn' | 'change' | 'research') {
  const config = {
    learn: {
      icon: '📚',
      color: 'bg-blue-50 border-blue-200 text-blue-900',
      label: '학습',
    },
    change: {
      icon: '🔄',
      color: 'bg-green-50 border-green-200 text-green-900',
      label: '변경',
    },
    research: {
      icon: '🔍',
      color: 'bg-purple-50 border-purple-200 text-purple-900',
      label: '조사',
    },
  }
  
  return config[type]
}

// 프로젝트 상태에 따른 배지 색상
export function getProjectStatusConfig(status: 'draft' | 'active' | 'archived' | 'deleted') {
  const config = {
    draft: {
      color: 'bg-gray-100 text-gray-800',
      label: '초안',
    },
    active: {
      color: 'bg-green-100 text-green-800',
      label: '활성',
    },
    archived: {
      color: 'bg-yellow-100 text-yellow-800',
      label: '보관',
    },
    deleted: {
      color: 'bg-red-100 text-red-800',
      label: '삭제',
    },
  }
  
  return config[status]
}

// 가시성에 따른 아이콘
export function getVisibilityIcon(visibility: 'public' | 'private' | 'unlisted') {
  const icons = {
    public: '🌍',
    private: '🔒',
    unlisted: '👁️‍🗨️',
  }
  
  return icons[visibility]
}