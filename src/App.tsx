import { Sidebar } from './components/Sidebar';
import { ProjectForm } from './components/ProjectForm';
import { QueryInbox } from './components/QueryInbox';
import { WikiView } from './components/WikiView';
import { useAppStore } from './stores/appStore';

function App() {
  const { selectedProjectId, view } = useAppStore();

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0">
        {selectedProjectId ? (
          view === 'wiki' ? <WikiView /> : <QueryInbox />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">📝</div>
              <h2 className="text-xl font-semibold text-slate-200 mb-2">
                Select or create a project
              </h2>
              <p className="text-sm text-slate-500 max-w-sm">
                Choose a project from the sidebar, or create a new one to start curating knowledge.
              </p>
            </div>
          </div>
        )}
      </main>
      <ProjectForm />
    </div>
  );
}

export default App;
