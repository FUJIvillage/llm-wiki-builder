import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listProjects, createProject, deleteProject } from '../lib/api';
import type { Project, ProjectSummary, CreateProjectPayload } from '../types';

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

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY] });
    },
  });
}
