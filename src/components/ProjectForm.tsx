import { useState } from 'react';
import { X } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { useCreateProject } from '../hooks/useProjects';

export function ProjectForm() {
  const { showProjectForm, setShowProjectForm } = useAppStore();
  const createProject = useCreateProject();
  const [form, setForm] = useState({
    name: '',
    raw_path: '',
    wiki_path: '',
    llm_endpoint: 'https://openrouter.ai/api/v1',
    llm_model: 'anthropic/claude-sonnet-4',
    llm_api_key: '',
  });

  if (!showProjectForm) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProject.mutateAsync(form);
      setShowProjectForm(false);
      setForm({
        name: '',
        raw_path: '',
        wiki_path: '',
        llm_endpoint: 'https://openrouter.ai/api/v1',
        llm_model: 'anthropic/claude-sonnet-4',
        llm_api_key: '',
      });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="w-full max-w-lg bg-slate-900 rounded-2xl border border-slate-700 p-6 m-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-slate-100">New Project</h2>
          <button
            onClick={() => setShowProjectForm(false)}
            className="text-slate-500 hover:text-slate-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1.5">Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50"
              placeholder="e.g. voice-calling-bot"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1.5">Raw Folder</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={form.raw_path}
                  onChange={(e) => setForm({ ...form, raw_path: e.target.value })}
                  className="flex-1 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50"
                  placeholder="/path/to/raw"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1.5">Wiki Folder</label>
              <input
                type="text"
                value={form.wiki_path}
                onChange={(e) => setForm({ ...form, wiki_path: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50"
                placeholder="/path/to/wiki"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1.5">LLM Endpoint</label>
            <input
              type="url"
              value={form.llm_endpoint}
              onChange={(e) => setForm({ ...form, llm_endpoint: e.target.value })}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1.5">Model</label>
            <input
              type="text"
              value={form.llm_model}
              onChange={(e) => setForm({ ...form, llm_model: e.target.value })}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1.5">API Key</label>
            <input
              type="password"
              value={form.llm_api_key}
              onChange={(e) => setForm({ ...form, llm_api_key: e.target.value })}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500/50"
              placeholder="sk-..."
              required
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setShowProjectForm(false)}
              className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createProject.isPending}
              className="px-6 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-sm font-semibold transition disabled:opacity-50"
            >
              {createProject.isPending ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
