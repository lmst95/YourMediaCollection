import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Star, Trash2, Edit, Plus, Clock } from 'lucide-react';
import { collectionsApi } from '../api/collections';
import EditCollectionModal from '../components/EditCollectionModal';
import CollectionTimeline from '../components/CollectionTimeline';
import type { CollectionStatus, UserMedia } from '../types';

const statusOptions: { value: CollectionStatus; label: string }[] = [
  { value: 'owned', label: 'Owned' },
  { value: 'watched', label: 'Watched' },
  { value: 'read', label: 'Read' },
  { value: 'listened', label: 'Listened' },
  { value: 'wishlist', label: 'Wishlist' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'borrowed', label: 'Borrowed' },
  { value: 'lent', label: 'Lent' },
];

interface GroupedMedia {
  mediaId: string;
  mediaDetails: any;
  items: UserMedia[];
}

export default function CollectionPageGrouped() {
  const [statusFilter, setStatusFilter] = useState<CollectionStatus | ''>('');
  const [page, setPage] = useState(1);
  const [editingItem, setEditingItem] = useState<UserMedia | null>(null);
  const [expandedMedia, setExpandedMedia] = useState<Set<string>>(new Set());
  const [showTimeline, setShowTimeline] = useState(false);
  const queryClient = useQueryClient();

  const { data: collection, isLoading } = useQuery(
    ['myCollection', statusFilter, page],
    () => collectionsApi.getMyCollection(statusFilter || undefined, page),
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
    if (confirm('Remove this status from your collection?')) {
      deleteMutation.mutate(id);
    }
  };

  const toggleExpanded = (mediaId: string) => {
    const newExpanded = new Set(expandedMedia);
    if (newExpanded.has(mediaId)) {
      newExpanded.delete(mediaId);
    } else {
      newExpanded.add(mediaId);
    }
    setExpandedMedia(newExpanded);
  };

  // Group items by media
  const groupedItems: GroupedMedia[] = collection?.results
    ? Object.values(
        collection.results.reduce((acc: { [key: string]: GroupedMedia }, item: UserMedia) => {
          // Skip items without media_details
          if (!item.media_details) return acc;

          const mediaId = item.media_details.id;
          if (!acc[mediaId]) {
            acc[mediaId] = {
              mediaId,
              mediaDetails: item.media_details,
              items: [],
            };
          }
          acc[mediaId].items.push(item);
          return acc;
        }, {})
      )
    : [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">My Collection</h1>
        <button
          onClick={() => setShowTimeline(!showTimeline)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            showTimeline
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          <Clock className="w-5 h-5" />
          {showTimeline ? 'Show Grid' : 'Show Timeline'}
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="card p-4">
            <p className="text-sm text-gray-600">Total Items</p>
            <p className="text-2xl font-bold">{stats.total_items}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600">Average Rating</p>
            <div className="flex items-center">
              <Star className="w-5 h-5 text-yellow-500 fill-current mr-1" />
              <p className="text-2xl font-bold">
                {stats.average_rating ? stats.average_rating.toFixed(1) : 'N/A'}
              </p>
            </div>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600">Books</p>
            <p className="text-2xl font-bold">{stats.by_type?.book || 0}</p>
          </div>
        </div>
      )}

      {/* Timeline View */}
      {showTimeline ? (
        <CollectionTimeline />
      ) : (
        <>
          {/* Status Filter */}
          <div className="mb-6">
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value as any);
            setPage(1);
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">All Status</option>
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Collection List - Grouped */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : collection && groupedItems.length > 0 ? (
        <div className="space-y-4">
          {groupedItems.map((group) => {
            const isExpanded = expandedMedia.has(group.mediaId);
            const firstItem = group.items[0];

            return (
              <div key={group.mediaId} className="card p-4">
                <div className="flex items-start gap-4">
                  {/* Cover Image */}
                  <div className="w-20 h-28 bg-gray-200 rounded flex-shrink-0">
                    {group.mediaDetails.cover_image_url ? (
                      <img
                        src={group.mediaDetails.cover_image_url}
                        alt={group.mediaDetails.title}
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
                      {group.mediaDetails.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {group.mediaDetails.media_type.replace('_', ' ')}
                    </p>

                    {/* Status Badges */}
                    <div className="flex flex-wrap gap-2 mb-2">
                      {group.items.map((item) => (
                        <span
                          key={item.id}
                          className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                        >
                          {item.status_display}
                        </span>
                      ))}
                    </div>

                    {/* Show first item's rating if available */}
                    {firstItem.rating && (
                      <div className="flex items-center text-yellow-600 mb-2">
                        <Star className="w-4 h-4 fill-current mr-1" />
                        <span className="text-sm">{firstItem.rating}/10</span>
                      </div>
                    )}

                    {/* Expand/Collapse for multiple items */}
                    {group.items.length > 1 && (
                      <button
                        onClick={() => toggleExpanded(group.mediaId)}
                        className="text-sm text-primary-600 hover:text-primary-700 mb-2"
                      >
                        {isExpanded ? '− Hide details' : `+ Show ${group.items.length} statuses`}
                      </button>
                    )}

                    {/* Expanded Details */}
                    {(isExpanded || group.items.length === 1) && (
                      <div className="mt-3 space-y-3 pt-3 border-t">
                        {group.items.map((item) => (
                          <div
                            key={item.id}
                            className="p-3 bg-gray-50 rounded-lg flex items-start justify-between"
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-medium text-sm">{item.status_display}</span>
                                {item.rating && (
                                  <div className="flex items-center text-yellow-600">
                                    <Star className="w-3 h-3 fill-current mr-1" />
                                    <span className="text-xs">{item.rating}/10</span>
                                  </div>
                                )}
                              </div>
                              {item.notes && (
                                <p className="text-sm text-gray-600 mb-1">{item.notes}</p>
                              )}
                              <p className="text-xs text-gray-500">
                                Added {new Date(item.added_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="flex items-center space-x-2 ml-4">
                              <button
                                onClick={() => {
                                  console.log('Edit clicked, item:', item);
                                  setEditingItem(item);
                                }}
                                className="p-2 text-gray-600 hover:text-primary-600 transition-colors"
                                title="Edit"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDelete(item.id)}
                                className="p-2 text-gray-600 hover:text-red-600 transition-colors"
                                title="Remove"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

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
        </>
      )}

      {/* Edit Collection Modal */}
      {editingItem && (
        <EditCollectionModal
          item={editingItem}
          isOpen={!!editingItem}
          onClose={() => setEditingItem(null)}
        />
      )}
    </div>
  );
}
