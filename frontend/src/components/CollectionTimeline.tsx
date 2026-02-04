import { useRef } from 'react';
import { useQuery } from 'react-query';
import { ChevronLeft, ChevronRight, Calendar, Star } from 'lucide-react';
import { collectionsApi } from '../api/collections';
import { Link } from 'react-router-dom';
import type { UserMediaCollection, CollectionFlag } from '../types';

const flagColors: Record<CollectionFlag, { bg: string; ring: string }> = {
  owned: { bg: 'bg-blue-500', ring: 'ring-blue-100' },
  wishlist: { bg: 'bg-yellow-500', ring: 'ring-yellow-100' },
  watched: { bg: 'bg-green-500', ring: 'ring-green-100' },
  in_progress: { bg: 'bg-purple-500', ring: 'ring-purple-100' },
};

export default function CollectionTimeline() {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const { data, isLoading } = useQuery('collectionTimeline', () =>
    collectionsApi.getTimeline()
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

  // Group by month
  const groupedByMonth = data?.results.reduce((acc: { [key: string]: UserMediaCollection[] }, item) => {
    const date = new Date(item.added_at);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    const monthLabel = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });

    if (!acc[monthLabel]) {
      acc[monthLabel] = [];
    }
    acc[monthLabel].push(item);
    return acc;
  }, {}) || {};

  const months = Object.keys(groupedByMonth).sort((a, b) => {
    const dateA = new Date(a);
    const dateB = new Date(b);
    return dateB.getTime() - dateA.getTime(); // Newest first
  });

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!data || data.results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No collection activity yet</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-1">Your Collection Activity</h2>
          <p className="text-gray-600">
            {data.count} items across {months.length} months
          </p>
        </div>
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

      <div className="relative">
        {/* Horizontal scrollable timeline */}
        <div
          ref={scrollContainerRef}
          className="flex gap-6 overflow-x-auto pb-8 scroll-smooth"
          style={{ scrollbarWidth: 'thin' }}
        >
          {months.map((month) => (
            <div key={month} className="flex-shrink-0" style={{ width: '300px' }}>
              {/* Month header */}
              <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-t-lg p-4 shadow-md">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  <h3 className="text-xl font-bold">{month}</h3>
                </div>
                <p className="text-sm text-green-100 mt-1">
                  {groupedByMonth[month].length} item{groupedByMonth[month].length !== 1 ? 's' : ''} added
                </p>
              </div>

              {/* Timeline items for this month */}
              <div className="bg-white rounded-b-lg shadow-md p-4 space-y-4 min-h-[400px]">
                {groupedByMonth[month].map((item, index) => (
                  <Link
                    key={item.id}
                    to={`/media/${item.media_details.id}`}
                    className="block group"
                  >
                    <div className="relative">
                      {/* Timeline connector */}
                      {index < groupedByMonth[month].length - 1 && (
                        <div className="absolute left-6 top-full w-0.5 h-4 bg-gray-200"></div>
                      )}

                      <div className="flex gap-3 hover:bg-gray-50 rounded-lg p-2 transition-colors">
                        {/* Timeline dot with primary flag color */}
                        <div className="flex-shrink-0 pt-1">
                          <div
                            className={`w-3 h-3 rounded-full ring-4 ${
                              item.status_flags.length > 0
                                ? `${flagColors[item.status_flags[0]]?.bg || 'bg-gray-500'} ${flagColors[item.status_flags[0]]?.ring || 'ring-gray-100'}`
                                : 'bg-gray-500 ring-gray-100'
                            }`}
                          ></div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          {/* Cover image */}
                          {item.media_details.cover_image_url && (
                            <div className="w-full h-32 bg-gray-200 rounded mb-2 overflow-hidden">
                              <img
                                src={item.media_details.cover_image_url}
                                alt={item.media_details.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                              />
                            </div>
                          )}

                          {/* Title */}
                          <h4 className="font-semibold text-sm text-gray-900 line-clamp-2 mb-1 group-hover:text-primary-600">
                            {item.media_details.title}
                          </h4>

                          {/* Property flags */}
                          <div className="flex flex-wrap gap-1 mb-1">
                            {item.status_flags.map((flag) => (
                              <span key={flag} className="inline-block px-2 py-0.5 bg-primary-100 text-primary-800 text-xs rounded">
                                {flag}
                              </span>
                            ))}
                          </div>

                          {/* Rating */}
                          {item.rating && (
                            <div className="flex items-center text-yellow-600 mt-1">
                              <Star className="w-3 h-3 fill-current mr-1" />
                              <span className="text-xs">{Number(item.rating).toFixed(1)}/10</span>
                            </div>
                          )}

                          {/* Notes preview */}
                          {item.notes && (
                            <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                              {item.notes}
                            </p>
                          )}

                          {/* Added date */}
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(item.added_at).toLocaleDateString()}
                          </p>
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
          ← Scroll horizontally to see your collection history →
        </div>
      </div>
    </div>
  );
}
