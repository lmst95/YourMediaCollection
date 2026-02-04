import { useState, useRef } from 'react';
import { useQuery } from 'react-query';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { mediaApi } from '../api/media';
import FilterBar from '../components/FilterBar';
import type { MediaFilters, Media } from '../types';
import { Link } from 'react-router-dom';

export default function TimelinePage() {
  const [filters, setFilters] = useState<MediaFilters>({});
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const { data, isLoading } = useQuery(
    ['timeline', filters],
    () => mediaApi.getTimeline(filters, 1),
    { keepPreviousData: true }
  );

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 400;
      scrollContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  // Group media by year
  const groupedByYear = data?.results.reduce((acc: { [year: string]: Media[] }, media) => {
    const year = media.release_date
      ? new Date(media.release_date).getFullYear().toString()
      : 'Unknown';
    if (!acc[year]) {
      acc[year] = [];
    }
    acc[year].push(media);
    return acc;
  }, {}) || {};

  const years = Object.keys(groupedByYear).sort((a, b) => {
    if (a === 'Unknown') return 1;
    if (b === 'Unknown') return -1;
    return parseInt(b) - parseInt(a); // Newest first
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Release Timeline</h1>
        <p className="text-gray-600">
          Explore media chronologically - scroll horizontally through the timeline
        </p>
      </div>

      <FilterBar onFilterChange={setFilters} />

      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {data && (
        <>
          <div className="mb-6 flex items-center justify-between">
            <p className="text-gray-600">
              {data.count} items across {years.length} years
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => scroll('left')}
                className="p-2 rounded-lg bg-white shadow hover:bg-gray-50 transition-colors"
                title="Scroll left"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={() => scroll('right')}
                className="p-2 rounded-lg bg-white shadow hover:bg-gray-50 transition-colors"
                title="Scroll right"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {years.length > 0 ? (
            <div className="relative">
              {/* Horizontal scrollable timeline */}
              <div
                ref={scrollContainerRef}
                className="flex gap-8 overflow-x-auto pb-8 scroll-smooth"
                style={{ scrollbarWidth: 'thin' }}
              >
                {years.map((year) => (
                  <div key={year} className="flex-shrink-0" style={{ width: '320px' }}>
                    {/* Year header */}
                    <div className="sticky top-0 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-t-lg p-4 shadow-md z-10">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-5 h-5" />
                        <h2 className="text-2xl font-bold">{year}</h2>
                      </div>
                      <p className="text-sm text-primary-100 mt-1">
                        {groupedByYear[year].length} item{groupedByYear[year].length !== 1 ? 's' : ''}
                      </p>
                    </div>

                    {/* Timeline items for this year */}
                    <div className="bg-white rounded-b-lg shadow-md p-4 space-y-4 min-h-[400px]">
                      {groupedByYear[year].map((media, index) => (
                        <Link
                          key={media.id}
                          to={`/media/${media.id}`}
                          className="block group"
                        >
                          <div className="relative">
                            {/* Timeline connector */}
                            {index < groupedByYear[year].length - 1 && (
                              <div className="absolute left-6 top-full w-0.5 h-4 bg-gray-200"></div>
                            )}

                            <div className="flex gap-3 hover:bg-gray-50 rounded-lg p-2 transition-colors">
                              {/* Timeline dot */}
                              <div className="flex-shrink-0 pt-1">
                                <div className="w-3 h-3 rounded-full bg-primary-500 ring-4 ring-primary-100"></div>
                              </div>

                              {/* Content */}
                              <div className="flex-1 min-w-0">
                                {/* Cover image */}
                                {media.cover_image_url && (
                                  <div className="w-full h-32 bg-gray-200 rounded mb-2 overflow-hidden">
                                    <img
                                      src={media.cover_image_url}
                                      alt={media.title}
                                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                    />
                                  </div>
                                )}

                                {/* Title */}
                                <h3 className="font-semibold text-sm text-gray-900 line-clamp-2 mb-1 group-hover:text-primary-600">
                                  {media.title}
                                </h3>

                                {/* Media type badge */}
                                <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                                  {media.media_type.replace('_', ' ')}
                                </span>

                                {/* Release date */}
                                {media.release_date && (
                                  <p className="text-xs text-gray-500 mt-1">
                                    {new Date(media.release_date).toLocaleDateString()}
                                  </p>
                                )}

                                {/* Description preview */}
                                {media.description && (
                                  <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                                    {media.description}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Scroll hint */}
              <div className="text-center mt-4 text-sm text-gray-500">
                ← Scroll horizontally to explore the timeline →
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              No items found in timeline
            </div>
          )}
        </>
      )}
    </div>
  );
}
