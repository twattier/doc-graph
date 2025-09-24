import { useState } from 'react';
import { Button } from '../components/ui/button';
import { RepositoryImportForm } from '../components/RepositoryImportForm';
import { ImportProgress } from '../components/ImportProgress';
import { RepositoryList } from '../components/RepositoryList';

export interface ImportStatus {
  id: string;
  url: string;
  status: 'pending' | 'cloning' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  startedAt: string;
  completedAt?: string;
}

export function RepositoryImportPage() {
  const [activeImports, setActiveImports] = useState<ImportStatus[]>([]);
  const [repositories, setRepositories] = useState<any[]>([]);
  const [showImportForm, setShowImportForm] = useState(false);

  const handleImportStart = (importStatus: ImportStatus) => {
    setActiveImports(prev => [...prev, importStatus]);
    setShowImportForm(false);
  };

  const handleImportUpdate = (id: string, updates: Partial<ImportStatus>) => {
    setActiveImports(prev =>
      prev.map(imp => imp.id === id ? { ...imp, ...updates } : imp)
    );
  };

  const handleImportComplete = (importStatus: ImportStatus, repository: any) => {
    setActiveImports(prev => prev.filter(imp => imp.id !== importStatus.id));
    setRepositories(prev => [...prev, repository]);
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Repository Import
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Import Git repositories for template-aware documentation analysis
        </p>

        <div className="flex gap-4">
          <Button
            onClick={() => setShowImportForm(true)}
            disabled={showImportForm}
          >
            Import Repository
          </Button>
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Import Form */}
      {showImportForm && (
        <div className="mb-8">
          <RepositoryImportForm
            onImportStart={handleImportStart}
            onCancel={() => setShowImportForm(false)}
          />
        </div>
      )}

      {/* Active Imports */}
      {activeImports.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Active Imports
          </h2>
          <div className="space-y-4">
            {activeImports.map((importStatus) => (
              <ImportProgress
                key={importStatus.id}
                importStatus={importStatus}
                onUpdate={(updates) => handleImportUpdate(importStatus.id, updates)}
                onComplete={(repository) => handleImportComplete(importStatus, repository)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Repository List */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Imported Repositories
        </h2>
        <RepositoryList
          repositories={repositories}
          onRefresh={() => {
            // TODO: Implement repository refresh
          }}
        />
      </div>
    </div>
  );
}