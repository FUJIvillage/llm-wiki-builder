import { useQuery } from '@tanstack/react-query';

interface SearchResult {
  type: 'query' | 'project';
  id: number;
  title: string;
  snippet: string;
  project_id: number;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
}

async function searchWiki(q: string): Promise<SearchResponse> {
  if (!q.trim()) return { query: q, results: [] };
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}

export function useSearch(q: string) {
  return useQuery({
    queryKey: ['search', q],
    queryFn: () => searchWiki(q),
    enabled: q.trim().length > 0,
  });
}
