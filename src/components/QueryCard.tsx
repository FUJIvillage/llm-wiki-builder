import { useState } from 'react';
import { SkipForward, Send } from 'lucide-react';
import { useSubmitAnswer, useSkipQuery } from '../hooks/useQueries';
import type { Query } from '../types';

interface QueryCardProps {
  query: Query;
}

export function QueryCard({ query }: QueryCardProps) {
  const submitAnswer = useSubmitAnswer();
  const skipQuery = useSkipQuery();
  const [selected, setSelected] = useState<string[]>([]);

  const handleToggle = (choiceId: string) => {
    if (query.query_type === 'multi_select') {
      setSelected((prev) =>
        prev.includes(choiceId)
          ? prev.filter((id) => id !== choiceId)
          : [...prev, choiceId]
      );
    } else {
      setSelected([choiceId]);
    }
  };

  const handleSubmit = () => {
    submitAnswer.mutate({
      query_id: query.id,
      selected_choice_ids: selected,
      free_text: null,
    });
  };

  const isAnswered = query.status !== 'pending';
  const canSubmit = selected.length > 0;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mb-1">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {query.query_type.replace('_', ' ')}
          </span>
        </div>
        <h2 className="text-xl font-semibold text-slate-100 mb-4 leading-relaxed">
          {query.question}
        </h2>
        {query.context && (
          <p className="text-sm text-slate-400 mb-6 bg-slate-900/50 rounded-lg p-3 border border-slate-800">
            {query.context}
          </p>
        )}

        <div className="space-y-2">
          {query.choices.map((choice) => {
            const isSelected = selected.includes(choice.id);
            return (
              <button
                key={choice.id}
                onClick={() => handleToggle(choice.id)}
                disabled={isAnswered}
                className={`w-full text-left px-4 py-3 rounded-xl border transition group ${
                  isSelected
                    ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-600 text-slate-300'
                } ${isAnswered ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition ${
                      query.query_type === 'multi_select'
                        ? isSelected
                          ? 'bg-cyan-500 border-cyan-500'
                          : 'border-slate-600'
                        : isSelected
                        ? 'border-cyan-500'
                        : 'border-slate-600'
                    }`}
                  >
                    {query.query_type === 'multi_select' && isSelected && (
                      <svg className="w-3 h-3 text-slate-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                    {query.query_type !== 'multi_select' && isSelected && (
                      <div className="w-2.5 h-2.5 rounded-full bg-cyan-500" />
                    )}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{choice.label}</div>
                    {choice.description && (
                      <div className="text-xs text-slate-500 mt-0.5">{choice.description}</div>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between">
        <button
          onClick={() => skipQuery.mutate({ query_id: query.id })}
          disabled={isAnswered || skipQuery.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition disabled:opacity-50"
        >
          <SkipForward className="w-4 h-4" />
          Skip
        </button>

        <button
          onClick={handleSubmit}
          disabled={!canSubmit || isAnswered || submitAnswer.isPending}
          className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-sm font-semibold transition disabled:opacity-40"
        >
          <Send className="w-4 h-4" />
          {submitAnswer.isPending ? 'Saving...' : 'Answer'}
        </button>
      </div>
    </div>
  );
}
