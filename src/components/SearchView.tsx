import { useState } from 'react';
import { Search, X, FileText, Folder } from 'lucide-react';
import { useSearch } from '../hooks/useSearch';
import { useAppStore } from '../stores/appStore';

export function SearchView() {
  const [query, setQuery] = useState('');
  const { data, isLoading } = useSearch(query);
  const { setSelectedProjectId, setView } = useAppStore();

  const handleResultClick = (result: { type: string; project_id: number }) => {
    setSelectedProjectId(String(result.project_id));
    if (result.type === 'query') {
      setView('inbox');
    } else {
      setView('wiki');
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Search Input */}
      <div className="p-4 border-b border-slate-800">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search queries, projects..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-10 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition"
            autoFocus
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-4">
        {!query && (
          <div className="text-center py-12">
            <Search className="w-10 h-10 text-slate-700 mx-auto mb-3" />
            <p className="text-sm text-slate-500">Type to search across all projects and queries</p>
          </div>
        )}

        {isLoading && query && (
          <div className="flex items-center justify-center py-8">
            <div className="text-sm text-slate-500">Searching...</div>
          </div>
        )}

        {data && data.results.length === 0 && query && (
          <div className="text-center py-8">
            <p className="text-sm text-slate-500">No results for "{query}"</p>
          </div>
        )}

        {data && data.results.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs text-slate-500 mb-3">
              {data.results.length} result{data.results.length !== 1 ? 's' : ''}
            </div>
            {data.results.map((result) => (
              <button
                key={`${result.type}-${result.id}`}
                onClick={() => handleResultClick(result)}
                className="w-full text-left p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-slate-600 hover:bg-slate-800/50 transition group"
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {result.type === 'project' ? (
                      <Folder className="w-4 h-4 text-violet-400" />
                    ) : (
                      <FileText className="w-4 h-4 text-cyan-400" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium text-slate-200 group-hover:text-cyan-300 transition">
                      {result.title}
                    </div>
                    {result.snippet && (
                      <div className="text-xs text-slate-500 mt-1 truncate">
                        {result.snippet}
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded border ${
                        result.type === 'project'
                          ? 'bg-violet-500/10 text-violet-400 border-violet-500/20'
                          : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                      }`}>
                        {result.type}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
