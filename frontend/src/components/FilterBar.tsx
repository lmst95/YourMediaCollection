import { useState, useEffect } from 'react';
import { Search, Filter, X } from 'lucide-react';
import type { MediaFilters, MediaType } from '../types';

interface FilterBarProps {
  onFilterChange: (filters: MediaFilters) => void;
  showAdvanced?: boolean;
  initialFilters?: MediaFilters;
}

const mediaTypes: { value: MediaType; label: string }[] = [
  { value: 'movie', label: 'Movies' },
  { value: 'tv_series', label: 'TV Series' },
  { value: 'book', label: 'Books' },
  { value: 'music', label: 'Music' },
  { value: 'concert', label: 'Concerts' },
  { value: 'document', label: 'Documents' },
];

export default function FilterBar({ onFilterChange, showAdvanced = true, initialFilters = {} }: FilterBarProps) {
  const [filters, setFilters] = useState<MediaFilters>(initialFilters);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Update local state when initialFilters change (e.g., from URL)
  useEffect(() => {
    if (Object.keys(initialFilters).length > 0) {
      setFilters(initialFilters);
    }
  }, [initialFilters]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onFilterChange(filters);
    }, 500); // Debounce filter changes

    return () => clearTimeout(timeoutId);
  }, [filters, onFilterChange]);

  const updateFilter = (key: keyof MediaFilters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const hasActiveFilters = Object.keys(filters).length > 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <div className="flex flex-col space-y-4">
        {/* Search and Media Type */}
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search Bar */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by title..."
              value={filters.title_contains || ''}
              onChange={(e) => updateFilter('title_contains', e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Media Type Filter */}
          <select
            value={filters.media_type || ''}
            onChange={(e) => updateFilter('media_type', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Types</option>
            {mediaTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>

          {showAdvanced && (
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Filter className="w-5 h-5" />
              <span>Filters</span>
            </button>
          )}

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Advanced Filters */}
        {showAdvanced && showAdvancedFilters && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t">
            {/* Genre Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
              <input
                type="text"
                placeholder="e.g., Action, Fantasy"
                value={filters.genre || ''}
                onChange={(e) => updateFilter('genre', e.target.value)}
                className="input"
              />
            </div>

            {/* Year Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Year</label>
              <input
                type="number"
                placeholder="e.g., 1990"
                value={filters.release_year_min || ''}
                onChange={(e) => updateFilter('release_year_min', e.target.value)}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Year</label>
              <input
                type="number"
                placeholder="e.g., 2024"
                value={filters.release_year_max || ''}
                onChange={(e) => updateFilter('release_year_max', e.target.value)}
                className="input"
              />
            </div>

            {/* Creator/Contributor Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author</label>
              <input
                type="text"
                placeholder="Book author"
                value={filters.author || ''}
                onChange={(e) => updateFilter('author', e.target.value)}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Artist</label>
              <input
                type="text"
                placeholder="Music artist"
                value={filters.artist || ''}
                onChange={(e) => updateFilter('artist', e.target.value)}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Director</label>
              <input
                type="text"
                placeholder="Movie director"
                value={filters.director || ''}
                onChange={(e) => updateFilter('director', e.target.value)}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Actor</label>
              <input
                type="text"
                placeholder="Actor name"
                value={filters.actor || ''}
                onChange={(e) => updateFilter('actor', e.target.value)}
                className="input"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Any Contributor
              </label>
              <input
                type="text"
                placeholder="Search across all creators"
                value={filters.contributor || ''}
                onChange={(e) => updateFilter('contributor', e.target.value)}
                className="input"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
