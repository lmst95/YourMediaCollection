import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Star, Trash2, Edit } from 'lucide-react';
import { collectionsApi } from '../api/collections';
import EditCollectionModal from '../components/EditCollectionModal';
import type { CollectionFlag, UserMediaCollection } from '../types';

const flagOptions: { value: CollectionFlag; label: string }[] = [
  { value: 'owned', label: 'Owned' },
  { value: 'wishlist', label: 'Wishlist' },
  { value: 'watched', label: 'Watched' },
  { value: 'in_progress', label: 'In Progress' },
];

const flagColors: Record<CollectionFlag, string> = {
  owned: 'bg-blue-100 text-blue-800',
  wishlist: 'bg-yellow-100 text-yellow-800',
  watched: 'bg-green-100 text-green-800',
  in_progress: 'bg-purple-100 text-purple-800',
};

export default function CollectionPage() {
  const [flagFilter, setFlagFilter] = useState<CollectionFlag | ''>('');
  const [page, setPage] = useState(1);
  const [editingItem, setEditingItem] = useState<UserMediaCollection | null>(null);
  const queryClient = useQueryClient();

  const { data: collection, isLoading } = useQuery(
    ['myCollection', flagFilter, page],
    () => collectionsApi.getMyCollection(flagFilter || undefined, page),
    { keepPreviousData: true }
  );

  const { data: stats } = useQuery('collectionStats', () => collectionsApi.getStats());

  const deleteMutation = useMutation(
    (id: string) => collectionsApi.removeFromCollection(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('myCollection');
        queryClient.invalidateQueries('collectionStats');
      },
    }
  );

  const handleDelete = (id: string) => {
    if (confirm('Remove this item from your collection?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">My Collection</h1>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          <div className="card p-4">
            <p className="text-sm text-gray-600">Total Items</p>
            <p className="text-2xl font-bold">{stats.total_items}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600">Owned</p>
            <p className="text-2xl font-bold">{stats.total_owned}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600">Wishlist</p>
            <p className="text-2xl font-bold">{stats.total_wishlist}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600">Watched</p>
            <p className="text-2xl font-bold">{stats.total_watched}</p>
          </div>
        </div>
      )}

      {/* Property Filter */}
      <div className="mb-6">
        <select
          value={flagFilter}
          onChange={(e) => { setFlagFilter(e.target.value as any); setPage(1); }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">All Items</option>
          {flagOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Collection List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : collection && collection.results.length > 0 ? (
        <div className="space-y-4">
          {collection.results.map((item: UserMediaCollection) => (
            <div key={item.id} className="card p-4 flex items-start gap-4">
              {/* Cover Image */}
              <div className="w-20 h-28 bg-gray-200 rounded flex-shrink-0">
                {item.media_details.cover_image_url ? (
                  <img
                    src={item.media_details.cover_image_url}
                    alt={item.media_details.title}
                    className="w-full h-full object-cover rounded"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-2xl">
                    📚
                  </div>
                )}
              </div>

              {/* Details */}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg text-gray-900 truncate">
                  {item.media_details.title}
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  {item.media_details.media_type.replace('_', ' ')}
                </p>

                {/* Property Flags */}
                <div className="flex flex-wrap gap-1 mb-2">
                  {item.status_flags.map((flag) => (
                    <span
                      key={flag}
                      className={`px-2 py-0.5 text-xs font-medium rounded ${flagColors[flag]}`}
                    >
                      {flagOptions.find(opt => opt.value === flag)?.label || flag}
                    </span>
                  ))}
                </div>

                {/* Lending Info */}
                {(item.active_lent_to.length > 0 || item.active_borrowed_from.length > 0) && (
                  <div className="text-xs text-gray-600 mb-2">
                    {item.active_lent_to.length > 0 && (
                      <span className="mr-2">📤 Lent to: {item.active_lent_to.join(', ')}</span>
                    )}
                    {item.active_borrowed_from.length > 0 && (
                      <span>📥 Borrowed from: {item.active_borrowed_from.join(', ')}</span>
                    )}
                  </div>
                )}

                {item.rating && (
                  <div className="flex items-center text-yellow-600 mb-2">
                    <Star className="w-4 h-4 fill-current mr-1" />
                    <span className="text-sm">{item.rating}/10</span>
                  </div>
                )}

                {item.notes && (
                  <p className="text-sm text-gray-600 line-clamp-2">{item.notes}</p>
                )}

                <p className="text-xs text-gray-500 mt-2">
                  Added {new Date(item.added_at).toLocaleDateString()}
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setEditingItem(item)}
                  className="p-2 text-gray-600 hover:text-primary-600 transition-colors"
                  title="Edit"
                >
                  <Edit className="w-5 h-5" />
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="p-2 text-gray-600 hover:text-red-600 transition-colors"
                  title="Remove"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}

          {/* Pagination */}
          {collection.count > 20 && (
            <div className="flex justify-center items-center space-x-4 mt-6">
              <button
                onClick={() => setPage(page - 1)}
                disabled={!collection.previous}
                className="btn btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-gray-600">
                Page {page} of {Math.ceil(collection.count / 20)}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={!collection.next}
                className="btn btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">Your collection is empty</p>
          <p className="text-sm">Start adding media to track what you own, watch, and read!</p>
        </div>
      )}

      {/* Edit Collection Modal */}
      <EditCollectionModal
        item={editingItem}
        isOpen={!!editingItem}
        onClose={() => setEditingItem(null)}
      />
    </div>
  );
}
