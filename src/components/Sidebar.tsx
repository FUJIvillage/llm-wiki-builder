import { Plus, Settings, Inbox, BookOpen, Search } from 'lucide-react';
import { useProjects } from '../hooks/useProjects';
import { useAppStore } from '../stores/appStore';

export function Sidebar() {
  const { data: projects, isLoading } = useProjects();
  const { selectedProjectId, setSelectedProjectId, setShowProjectForm, view, setView } = useAppStore();

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-full">
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-7 h-7 rounded bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center text-xs font-bold text-white">
            W
          </div>
          <h1 className="font-bold text-sm tracking-tight text-slate-100">LLM Wiki Builder</h1>
        </div>
        <p className="text-xs text-slate-500">v1.0.0-alpha</p>
      </div>

      <div className="flex-1 overflow-y-auto py-2">
        <div className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Projects
        </div>

        {isLoading && (
          <div className="px-4 py-2 text-xs text-slate-500">Loading...</div>
        )}

        {projects?.map((project) => (
          <button
            key={project.id}
            onClick={() => setSelectedProjectId(project.id)}
            className={`w-full text-left px-3 py-2.5 mx-2 rounded-lg transition group ${
              selectedProjectId === project.id
                ? 'bg-cyan-500/10 border border-cyan-500/20'
                : 'hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className={`text-sm font-medium ${
                  selectedProjectId === project.id ? 'text-cyan-400' : 'text-slate-300'
                }`}>
                  {project.name}
                </div>
                <div className="text-xs text-slate-600 mt-0.5">
                  {project.pending_query_count} queries pending
                </div>
              </div>
              {selectedProjectId === project.id && (
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              )}
            </div>
          </button>
        ))}

        <button
          onClick={() => setShowProjectForm(true)}
          className="w-full text-left px-3 py-2 mt-3 mx-2 rounded-lg border border-dashed border-slate-700 hover:border-slate-500 hover:bg-slate-800/30 transition flex items-center gap-2 text-slate-400 hover:text-slate-200"
        >
          <Plus className="w-4 h-4" />
          <span className="text-sm">New Project</span>
        </button>

        {selectedProjectId && (
          <>
            <div className="px-3 mt-6 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              View
            </div>
            <div className="px-2 space-y-1">
              <button
                onClick={() => setView('search')}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition text-sm ${
                  view === 'search'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <Search className="w-4 h-4" />
                Search
              </button>
              <button
                onClick={() => setView('inbox')}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition text-sm ${
                  view === 'inbox'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <Inbox className="w-4 h-4" />
                Query Inbox
              </button>
              <button
                onClick={() => setView('wiki')}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition text-sm ${
                  view === 'wiki'
                    ? 'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                Wiki
              </button>
            </div>
          </>
        )}
      </div>

      <div className="p-3 border-t border-slate-800">
        <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-800 transition text-slate-400 hover:text-slate-200">
          <Settings className="w-4 h-4" />
          <span className="text-sm">Settings</span>
        </button>
      </div>
    </aside>
  );
}
