import { useEffect } from 'react';
import { ImportStatus } from '../pages/RepositoryImportPage';

interface ImportProgressProps {
  importStatus: ImportStatus;
  onUpdate: (updates: Partial<ImportStatus>) => void;
  onComplete: (repository: any) => void;
}

export function ImportProgress({ importStatus, onUpdate, onComplete }: ImportProgressProps) {
  useEffect(() => {
    if (importStatus.status === 'completed' || importStatus.status === 'failed') {
      return;
    }

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/repositories/${importStatus.id}/status`);
        if (!response.ok) {
          onUpdate({
            status: 'failed',
            message: 'Failed to get import status'
          });
          return;
        }

        const statusData = await response.json();

        onUpdate({
          status: statusData.status,
          progress: statusData.progress,
          message: statusData.message
        });

        if (statusData.status === 'completed') {
          onComplete(statusData.repository);
        }
      } catch (error) {
        onUpdate({
          status: 'failed',
          message: 'Network error while checking status'
        });
      }
    };

    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [importStatus.id, importStatus.status, onUpdate, onComplete]);

  const getStatusColor = () => {
    switch (importStatus.status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'cloning':
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = () => {
    switch (importStatus.status) {
      case 'completed':
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <div className="w-5 h-5">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          </div>
        );
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <h4 className="text-sm font-medium text-gray-900 truncate max-w-md">
              {importStatus.url}
            </h4>
            <p className="text-sm text-gray-500">
              Started {new Date(importStatus.startedAt).toLocaleTimeString()}
            </p>
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor()}`}>
          {importStatus.status.toUpperCase()}
        </span>
      </div>

      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm text-gray-500">{importStatus.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              importStatus.status === 'failed'
                ? 'bg-red-500'
                : importStatus.status === 'completed'
                ? 'bg-green-500'
                : 'bg-blue-500'
            }`}
            style={{ width: `${importStatus.progress}%` }}
          ></div>
        </div>
      </div>

      <p className="text-sm text-gray-600">{importStatus.message}</p>

      {importStatus.status === 'failed' && (
        <div className="mt-3 p-3 bg-red-50 rounded-md">
          <p className="text-sm text-red-700">
            Import failed. Please check the repository URL and try again.
          </p>
        </div>
      )}

      {importStatus.status === 'completed' && (
        <div className="mt-3 p-3 bg-green-50 rounded-md">
          <p className="text-sm text-green-700">
            Repository imported successfully! You can now analyze its documentation templates.
          </p>
        </div>
      )}
    </div>
  );
}