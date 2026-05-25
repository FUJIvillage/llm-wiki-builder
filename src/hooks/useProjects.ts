import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listProjects, createProject } from '../lib/api';

const PROJECTS_KEY = 'projects';

export function useProjects() {
  return useQuery({
    queryKey: [PROJECTS_KEY],
    queryFn: listProjects,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY] });
    },
  });
}
