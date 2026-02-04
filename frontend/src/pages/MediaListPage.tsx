import { useState, useEffect, useMemo } from 'react';
import { useQuery } from 'react-query';
import { useSearchParams } from 'react-router-dom';
import { mediaApi } from '../api/media';
import MediaCard from '../components/MediaCard';
import FilterBar from '../components/FilterBar';
import type { MediaFilters } from '../types';

export default function MediaListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [page, setPage] = useState(1);

  // Parse filters from URL params - this updates when URL changes
  const filtersFromUrl = useMemo(() => {
    const initialFilters: MediaFilters = {};
    const mediaType = searchParams.get('media_type');
    const genre = searchParams.get('genre');
    const author = searchParams.get('author');
    const artist = searchParams.get('artist');
    const director = searchParams.get('director');
    const actor = searchParams.get('actor');
    const titleContains = searchParams.get('title_contains');
    const releaseYearMin = searchParams.get('release_year_min');
    const releaseYearMax = searchParams.get('release_year_max');

    if (mediaType) initialFilters.media_type = mediaType as any;
    if (genre) initialFilters.genre = genre;
    if (author) initialFilters.author = author;
    if (artist) initialFilters.artist = artist;
    if (director) initialFilters.director = director;
    if (actor) initialFilters.actor = actor;
    if (titleContains) initialFilters.title_contains = titleContains;
    if (releaseYearMin) initialFilters.release_year_min = releaseYearMin;
    if (releaseYearMax) initialFilters.release_year_max = releaseYearMax;

    return initialFilters;
  }, [searchParams]);

  const [filters, setFilters] = useState<MediaFilters>(filtersFromUrl);

  // Sync filters when URL changes
  useEffect(() => {
    setFilters(filtersFromUrl);
    setPage(1);
  }, [filtersFromUrl]);

  const { data, isLoading, error } = useQuery(
    ['media', filters, page],
    () => mediaApi.getMedia(filters, page),
    { keepPreviousData: true }
  );

  const handleFilterChange = (newFilters: MediaFilters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change

    // Update URL params
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) params.set(key, String(value));
    });
    setSearchParams(params);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Browse Media</h1>

      <FilterBar onFilterChange={handleFilterChange} initialFilters={filters} />

      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-600">Loading media...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          Error loading media. Please try again.
        </div>
      )}

      {data && (
        <>
          {/* Results Info */}
          <div className="flex items-center justify-between mb-6">
            <p className="text-gray-600">
              Showing {data.results.length} of {data.count} results
            </p>
          </div>

          {/* Media Grid */}
          {data.results.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {data.results.map((media) => (
                <MediaCard key={media.id} media={media} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No media found matching your filters.</p>
              <p className="text-gray-400 mt-2">Try adjusting your search criteria.</p>
            </div>
          )}

          {/* Pagination */}
          {data.count > 20 && (
            <div className="flex justify-center items-center space-x-4 mt-8">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={!data.previous}
                className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>

              <span className="text-gray-600">
                Page {page} of {Math.ceil(data.count / 20)}
              </span>

              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={!data.next}
                className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
