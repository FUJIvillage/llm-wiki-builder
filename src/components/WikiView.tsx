import { useQuery } from '@tanstack/react-query';
import { BookOpen, Clock, Hash } from 'lucide-react';
import { getWikiPage } from '../lib/api';
import { useAppStore } from '../stores/appStore';

function renderMarkdown(content: string): JSX.Element {
  const lines = content.split('\n');
  const elements: JSX.Element[] = [];
  let key = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith('# ')) {
      elements.push(
        <h1 key={key++} className="text-2xl font-bold text-slate-100 mb-4 mt-2">
          {line.replace('# ', '')}
        </h1>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <h2 key={key++} className="text-lg font-semibold text-cyan-400 mt-6 mb-3 pb-2 border-b border-slate-800">
          {line.replace('## ', '')}
        </h2>
      );
    } else if (line.startsWith('**') && line.endsWith('**')) {
      elements.push(
        <p key={key++} className="text-sm text-slate-300 my-2 font-medium">
          {line.replace(/\*\*/g, '')}
        </p>
      );
    } else if (line.startsWith('*Sources:*')) {
      elements.push(
        <p key={key++} className="text-xs text-slate-500 my-2 italic">
          {line}
        </p>
      );
    } else if (line.startsWith('*Generated')) {
      elements.push(
        <p key={key++} className="text-xs text-slate-500 my-3 italic">
          {line}
        </p>
      );
    } else if (line === '---') {
      elements.push(
        <hr key={key++} className="border-slate-800 my-4" />
      );
    } else if (line.trim() === '') {
      elements.push(<div key={key++} className="h-2" />);
    } else {
      elements.push(
        <p key={key++} className="text-sm text-slate-400 leading-relaxed">
          {line}
        </p>
      );
    }
  }

  return <>{elements}</>;
}

export function WikiView() {
  const { selectedProjectId } = useAppStore();

  const { data: wiki, isLoading } = useQuery({
    queryKey: ['wiki', selectedProjectId],
    queryFn: () => getWikiPage(selectedProjectId!),
    enabled: !!selectedProjectId,
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-slate-500 text-sm">Loading wiki...</div>
      </div>
    );
  }

  if (!wiki) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="text-5xl mb-3">📚</div>
          <h2 className="text-lg font-semibold text-slate-200 mb-1">No Wiki Yet</h2>
          <p className="text-sm text-slate-500 max-w-xs">
            Answer queries in the Inbox to build your wiki. Answered queries will be integrated here automatically.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Left: Answered Queries Summary */}
      <div className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-violet-400" />
            Wiki Contents
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
            <Hash className="w-3 h-3" />
            {wiki.source_queries} answered queries
          </div>
          {/* Query summaries would go here */}
          <div className="text-xs text-slate-600 p-2 rounded bg-slate-800/50 border border-slate-800">
            Query summaries and table of contents coming in next iteration.
          </div>
        </div>
        <div className="p-3 border-t border-slate-800 text-xs text-slate-600 flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          Updated {new Date(wiki.updated_at).toLocaleDateString()}
        </div>
      </div>

      {/* Right: Wiki Content */}
      <div className="flex-1 overflow-y-auto bg-slate-950">
        <div className="max-w-3xl mx-auto p-8">
          {renderMarkdown(wiki.content)}
        </div>
      </div>
    </div>
  );
}
