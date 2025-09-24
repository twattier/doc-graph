import { useState } from 'react';
import { Button } from './ui/button';
import { ImportStatus } from '../pages/RepositoryImportPage';

interface RepositoryImportFormProps {
  onImportStart: (importStatus: ImportStatus) => void;
  onCancel: () => void;
}

export function RepositoryImportForm({ onImportStart, onCancel }: RepositoryImportFormProps) {
  const [url, setUrl] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateRepositoryUrl = (url: string): boolean => {
    if (!url.trim()) {
      setValidationError('Repository URL is required');
      return false;
    }

    // Support GitHub, GitLab, Bitbucket patterns
    const patterns = [
      /^https:\/\/github\.com\/[\w\-._]+\/[\w\-._]+(?:\.git)?$/,
      /^https:\/\/gitlab\.com\/[\w\-._\/]+(?:\.git)?$/,
      /^https:\/\/bitbucket\.org\/[\w\-._]+\/[\w\-._]+(?:\.git)?$/,
      /^git@github\.com:[\w\-._]+\/[\w\-._]+\.git$/,
      /^git@gitlab\.com:[\w\-._\/]+\.git$/,
      /^git@bitbucket\.org:[\w\-._]+\/[\w\-._]+\.git$/
    ];

    const isValid = patterns.some(pattern => pattern.test(url.trim()));

    if (!isValid) {
      setValidationError(
        'Please enter a valid Git repository URL from GitHub, GitLab, or Bitbucket'
      );
      return false;
    }

    setValidationError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateRepositoryUrl(url)) {
      return;
    }

    setIsValidating(true);

    try {
      // Start the import process
      const response = await fetch('/api/repositories/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (!response.ok) {
        const error = await response.json();
        setValidationError(error.message || 'Failed to start import');
        return;
      }

      const { importId } = await response.json();

      // Create import status
      const importStatus: ImportStatus = {
        id: importId,
        url: url.trim(),
        status: 'pending',
        progress: 0,
        message: 'Initializing import...',
        startedAt: new Date().toISOString(),
      };

      onImportStart(importStatus);
    } catch (error) {
      setValidationError('Network error: Unable to start import');
    } finally {
      setIsValidating(false);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
    if (validationError) {
      setValidationError(null);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Import New Repository
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="repo-url" className="block text-sm font-medium text-gray-700 mb-2">
            Repository URL
          </label>
          <input
            id="repo-url"
            type="text"
            value={url}
            onChange={handleUrlChange}
            placeholder="https://github.com/username/repository"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isValidating}
          />
          {validationError && (
            <p className="mt-1 text-sm text-red-600">{validationError}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            Supports public repositories from GitHub, GitLab, and Bitbucket
          </p>
        </div>

        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={isValidating || !url.trim()}
          >
            {isValidating ? 'Validating...' : 'Start Import'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isValidating}
          >
            Cancel
          </Button>
        </div>
      </form>

      <div className="mt-4 p-3 bg-blue-50 rounded-md">
        <h4 className="text-sm font-medium text-blue-900 mb-2">Supported URL formats:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• https://github.com/username/repository</li>
          <li>• https://gitlab.com/username/repository</li>
          <li>• https://bitbucket.org/username/repository</li>
        </ul>
      </div>
    </div>
  );
}