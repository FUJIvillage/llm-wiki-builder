import { useState } from 'react';
import { Database, Sparkles, Inbox, ChevronRight } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { useQueries, useGenerateQueries } from '../hooks/useQueries';
import { QueryCard } from './QueryCard';

export function QueryInbox() {
  const { selectedProjectId } = useAppStore();
  const [selectedQueryId, setSelectedQueryId] = useState<string | null>(null);

  const { data: queries, isLoading } = useQueries({
    project_id: selectedProjectId || '',
    status: null,
    limit: 50,
    offset: 0,
  });

  const generateQueries = useGenerateQueries();

  const selectedQuery = queries?.find((q) => q.id === selectedQueryId) ?? queries?.[0];

  const handleGenerate = () => {
    if (selectedProjectId) {
      generateQueries.mutate(selectedProjectId);
    }
  };

  return (
    <div className="flex h-full">
      {/* Query List */}
      <div className="w-80 border-r border-slate-800 bg-slate-900/30 flex flex-col">
        <div className="h-14 border-b border-slate-800 flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Inbox className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium">Query Inbox</span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 text-xs border border-rose-500/20">
            {queries?.filter((q) => q.status === 'pending').length ?? 0} pending
          </span>
        </div>
        <div className="flex-1 overflow-y-auto">
          {isLoading && (
            <div className="flex items-center justify-center h-32 text-sm text-slate-500">
              Loading queries...
            </div>
          )}
          {!isLoading && (!queries || queries.length === 0) && (
            <div className="text-center py-8">
              <Database className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-500 mb-1">No queries yet</p>
              <p className="text-xs text-slate-600">
                Generate queries from your raw files to get started
              </p>
            </div>
          )}
          {queries?.map((query) => (
            <button
              key={query.id}
              onClick={() => setSelectedQueryId(query.id)}
              className={`w-full text-left px-4 py-3 border-b border-slate-800/50 transition group ${
                selectedQuery?.id === query.id
                  ? 'bg-cyan-500/5 border-l-2 border-l-cyan-500'
                  : 'hover:bg-slate-800/30 border-l-2 border-l-transparent'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className={`text-sm font-medium truncate ${
                    query.status === 'pending' ? 'text-slate-200' : 'text-slate-500'
                  }`}>
                    {query.question}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      query.status === 'pending'
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        : query.status === 'answered'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-slate-700/30 text-slate-500 border-slate-700/30'
                    }`}>
                      {query.status}
                    </span>
                    {query.priority_score > 0.7 && (
                      <span className="text-[10px] text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20">
                        high
                      </span>
                    )}
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-600 flex-shrink-0 mt-0.5" />
              </div>
            </button>
          ))}
        </div>
        <div className="p-3 border-t border-slate-800">
          <button
            onClick={handleGenerate}
            disabled={generateQueries.isPending}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-violet-500/10 hover:bg-violet-500/20 text-violet-400 text-sm font-medium border border-violet-500/20 transition disabled:opacity-40"
          >
            <Sparkles className="w-4 h-4" />
            {generateQueries.isPending ? 'Generating...' : 'Generate Queries'}
          </button>
        </div>
      </div>

      {/* Answer Panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {selectedQuery ? (
          <QueryCard query={selectedQuery} />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="text-5xl mb-4">💡</div>
              <h3 className="text-lg font-semibold text-slate-200 mb-2">
                {queries && queries.length > 0 ? 'Select a query' : 'Ready to curate knowledge'}
              </h3>
              <p className="text-sm text-slate-500 max-w-md">
                Select a project to begin
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
