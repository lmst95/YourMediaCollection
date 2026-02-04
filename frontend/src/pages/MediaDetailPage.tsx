import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Calendar, Star, ArrowLeft, Plus } from 'lucide-react';
import { mediaApi } from '../api/media';
import { authApi } from '../api/auth';
import AddToCollectionModal from '../components/AddToCollectionModal';

export default function MediaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const isAuthenticated = authApi.isAuthenticated();
  const [showCollectionModal, setShowCollectionModal] = useState(false);

  const { data: media, isLoading } = useQuery(
    ['media', id],
    () => mediaApi.getMediaById(id!),
    { enabled: !!id }
  );

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!media) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Media not found</p>
        <Link to="/media" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          ← Back to browse
        </Link>
      </div>
    );
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div>
      <Link
        to="/media"
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5 mr-1" />
        Back to browse
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Cover Image */}
        <div className="md:col-span-1">
          <div className="card sticky top-4">
            <div className="aspect-[2/3] bg-gray-200">
              {media.cover_image_url ? (
                <img
                  src={media.cover_image_url}
                  alt={media.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <span className="text-8xl">📚</span>
                </div>
              )}
            </div>

            {isAuthenticated && (
              <div className="p-4 space-y-2">
                <button
                  onClick={() => setShowCollectionModal(true)}
                  className="btn btn-primary w-full"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Add to Collection
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Add to Collection Modal */}
        {media && (
          <AddToCollectionModal
            media={media}
            isOpen={showCollectionModal}
            onClose={() => setShowCollectionModal(false)}
          />
        )}

        {/* Details */}
        <div className="md:col-span-2 space-y-6">
          {/* Title and Type */}
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium">
                {media.media_type.replace('_', ' ')}
              </span>
              {media.metadata?.vote_average && (
                <div className="flex items-center text-yellow-600">
                  <Star className="w-5 h-5 mr-1 fill-current" />
                  <span className="font-semibold">
                    {Number(media.metadata.vote_average).toFixed(1)}
                  </span>
                </div>
              )}
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{media.title}</h1>
            <div className="flex items-center text-gray-600">
              <Calendar className="w-5 h-5 mr-2" />
              <span>{formatDate(media.release_date)}</span>
            </div>
          </div>

          {/* Genres */}
          {media.genres && media.genres.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Genres</h3>
              <div className="flex flex-wrap gap-2">
                {media.genres.map((genre, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {media.description && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Description</h3>
              <p className="text-gray-700 leading-relaxed">{media.description}</p>
            </div>
          )}

          {/* Media-specific details */}
          {media.metadata && Object.keys(media.metadata).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Details</h3>
              <div className="grid grid-cols-2 gap-4">
                {media.metadata.cast && Array.isArray(media.metadata.cast) && (
                  <div>
                    <p className="text-sm text-gray-500">Cast</p>
                    <p className="text-gray-900">
                      {media.metadata.cast.slice(0, 3).map((c: any) => c.name).join(', ')}
                    </p>
                  </div>
                )}
                {media.metadata.popularity && (
                  <div>
                    <p className="text-sm text-gray-500">Popularity</p>
                    <p className="text-gray-900">{Number(media.metadata.popularity).toFixed(0)}</p>
                  </div>
                )}
                {media.metadata.vote_count && (
                  <div>
                    <p className="text-sm text-gray-500">Vote Count</p>
                    <p className="text-gray-900">{media.metadata.vote_count}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
