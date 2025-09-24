import { Button } from './ui/button';

interface Repository {
  id: string;
  name: string;
  url: string;
  description?: string;
  importedAt: string;
  lastSyncedAt?: string;
  fileCount: number;
  templateCount: number;
  status: 'active' | 'syncing' | 'error';
}

interface RepositoryListProps {
  repositories: Repository[];
  onRefresh: () => void;
}

export function RepositoryList({ repositories, onRefresh }: RepositoryListProps) {
  const handleSync = async (repositoryId: string) => {
    try {
      await fetch(`/api/repositories/${repositoryId}/sync`, {
        method: 'PUT'
      });
      onRefresh();
    } catch (error) {
      console.error('Failed to sync repository:', error);
    }
  };

  const handleDelete = async (repositoryId: string) => {
    if (!confirm('Are you sure you want to delete this repository? This action cannot be undone.')) {
      return;
    }

    try {
      await fetch(`/api/repositories/${repositoryId}`, {
        method: 'DELETE'
      });
      onRefresh();
    } catch (error) {
      console.error('Failed to delete repository:', error);
    }
  };

  const getStatusBadge = (status: Repository['status']) => {
    switch (status) {
      case 'active':
        return (
          <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">
            Active
          </span>
        );
      case 'syncing':
        return (
          <span className="px-2 py-1 text-xs font-semibold text-blue-800 bg-blue-100 rounded-full">
            Syncing
          </span>
        );
      case 'error':
        return (
          <span className="px-2 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">
            Error
          </span>
        );
      default:
        return null;
    }
  };

  if (repositories.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <svg
          className="w-12 h-12 text-gray-400 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No repositories imported</h3>
        <p className="text-gray-500">
          Import your first Git repository to start analyzing documentation templates
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {repositories.map((repository) => (
        <div
          key={repository.id}
          className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-lg font-semibold text-gray-900">
                  {repository.name}
                </h3>
                {getStatusBadge(repository.status)}
              </div>

              <p className="text-sm text-gray-600 mb-3">{repository.url}</p>

              {repository.description && (
                <p className="text-gray-700 mb-3">{repository.description}</p>
              )}

              <div className="flex items-center space-x-6 text-sm text-gray-500 mb-4">
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a2 2 0 11-4 0 2 2 0 014 0zm8 0a2 2 0 11-4 0 2 2 0 014 0z" clipRule="evenodd" />
                  </svg>
                  {repository.fileCount} files
                </span>
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  {repository.templateCount} templates
                </span>
                <span>
                  Imported {new Date(repository.importedAt).toLocaleDateString()}
                </span>
                {repository.lastSyncedAt && (
                  <span>
                    Last synced {new Date(repository.lastSyncedAt).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>

            <div className="flex space-x-2 ml-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSync(repository.id)}
                disabled={repository.status === 'syncing'}
              >
                {repository.status === 'syncing' ? 'Syncing...' : 'Sync'}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  // TODO: Navigate to repository analysis page
                  console.log('Analyze repository:', repository.id);
                }}
              >
                Analyze
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDelete(repository.id)}
                className="text-red-600 border-red-200 hover:bg-red-50"
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}