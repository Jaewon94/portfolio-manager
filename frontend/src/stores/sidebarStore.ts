import { create } from 'zustand';

interface SidebarState {
  mobileOpen: boolean;
  collapsed: boolean;
  toggleMobile: () => void;
  closeMobile: () => void;
  toggleCollapsed: () => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  mobileOpen: false,
  collapsed: false,
  toggleMobile: () => set((state) => ({ mobileOpen: !state.mobileOpen })),
  closeMobile: () => set({ mobileOpen: false }),
  toggleCollapsed: () => set((state) => ({ collapsed: !state.collapsed })),
}));