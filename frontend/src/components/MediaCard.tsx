import { Link } from 'react-router-dom';
import { Calendar, Star } from 'lucide-react';
import type { Media } from '../types';

interface MediaCardProps {
  media: Media;
}

const mediaTypeColors: Record<string, string> = {
  movie: 'bg-purple-100 text-purple-800',
  tv_series: 'bg-blue-100 text-blue-800',
  book: 'bg-green-100 text-green-800',
  music: 'bg-pink-100 text-pink-800',
  concert: 'bg-orange-100 text-orange-800',
  document: 'bg-gray-100 text-gray-800',
};

export default function MediaCard({ media }: MediaCardProps) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
  };

  const typeColor = mediaTypeColors[media.media_type] || 'bg-gray-100 text-gray-800';

  return (
    <Link to={`/media/${media.id}`} className="card hover:shadow-lg transition-shadow">
      {/* Cover Image */}
      <div className="aspect-[2/3] bg-gray-200 relative overflow-hidden">
        {media.cover_image_url ? (
          <img
            src={media.cover_image_url}
            alt={media.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-6xl">📚</span>
          </div>
        )}

        {/* Media Type Badge */}
        <div className="absolute top-2 left-2">
          <span className={`px-2 py-1 text-xs font-medium rounded ${typeColor}`}>
            {media.media_type.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-2 mb-2">{media.title}</h3>

        {/* Release Date */}
        <div className="flex items-center text-sm text-gray-600 mb-2">
          <Calendar className="w-4 h-4 mr-1" />
          <span>{formatDate(media.release_date)}</span>
        </div>

        {/* Genres */}
        {media.genres && media.genres.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {media.genres.slice(0, 3).map((genre, index) => (
              <span
                key={index}
                className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded"
              >
                {genre}
              </span>
            ))}
            {media.genres.length > 3 && (
              <span className="px-2 py-0.5 text-xs text-gray-500">
                +{media.genres.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Rating (if available in metadata) */}
        {media.metadata?.vote_average && (
          <div className="flex items-center text-sm text-yellow-600">
            <Star className="w-4 h-4 mr-1 fill-current" />
            <span>{Number(media.metadata.vote_average).toFixed(1)}</span>
          </div>
        )}

        {/* Description Preview */}
        {media.description && (
          <p className="text-sm text-gray-600 line-clamp-2 mt-2">{media.description}</p>
        )}
      </div>
    </Link>
  );
}
