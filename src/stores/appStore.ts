import { create } from 'zustand';

interface AppState {
  selectedProjectId: string | null;
  setSelectedProjectId: (id: string | null) => void;
  view: 'inbox' | 'wiki' | 'settings' | 'search';
  setView: (view: 'inbox' | 'wiki' | 'settings' | 'search') => void;
  showProjectForm: boolean;
  setShowProjectForm: (show: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedProjectId: null,
  setSelectedProjectId: (id) => set({ selectedProjectId: id }),
  view: 'inbox',
  setView: (view) => set({ view }),
  showProjectForm: false,
  setShowProjectForm: (show) => set({ showProjectForm: show }),
}));
