import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listQueries, submitAnswer, skipQuery, generateQueries } from '../lib/api';
import type { ListQueriesPayload } from '../types';

const QUERIES_KEY = 'queries';

export function useQueries(payload: ListQueriesPayload) {
  return useQuery({
    queryKey: [QUERIES_KEY, payload.project_id, payload.status],
    queryFn: () => listQueries(payload),
    enabled: !!payload.project_id,
  });
}

export function useSubmitAnswer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitAnswer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERIES_KEY] });
    },
  });
}

export function useSkipQuery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: skipQuery,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERIES_KEY] });
    },
  });
}

export function useGenerateQueries() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: generateQueries,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERIES_KEY] });
    },
  });
}
