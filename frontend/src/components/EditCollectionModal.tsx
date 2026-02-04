import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { X, Star } from 'lucide-react';
import { collectionsApi } from '../api/collections';
import type { CollectionFlag, UserMediaCollection } from '../types';

interface EditCollectionModalProps {
  item: UserMediaCollection | null;
  isOpen: boolean;
  onClose: () => void;
}

const flagOptions: { value: CollectionFlag; label: string; description: string }[] = [
  { value: 'owned', label: 'Owned', description: 'I own this item' },
  { value: 'wishlist', label: 'Wishlist', description: 'I want to get this' },
  { value: 'watched', label: 'Watched/Read/Listened', description: 'I have consumed this media' },
  { value: 'in_progress', label: 'In Progress', description: 'Currently watching/reading/listening' },
];

export default function EditCollectionModal({ item, isOpen, onClose }: EditCollectionModalProps) {
  const queryClient = useQueryClient();
  const [selectedFlags, setSelectedFlags] = useState<CollectionFlag[]>([]);
  const [rating, setRating] = useState<number>(0);
  const [notes, setNotes] = useState('');
  const [watchedAt, setWatchedAt] = useState('');

  useEffect(() => {
    if (item) {
      try {
        // Set flags based on boolean properties
        const flags: CollectionFlag[] = [];
        if (item.is_owned) flags.push('owned');
        if (item.is_wishlist) flags.push('wishlist');
        if (item.is_watched) flags.push('watched');
        if (item.is_in_progress) flags.push('in_progress');

        setSelectedFlags(flags.length > 0 ? flags : ['wishlist']);
        setRating(item.rating || 0);
        setNotes(item.notes || '');
        setWatchedAt(item.watched_at ? item.watched_at.split('T')[0] : '');
      } catch (error) {
        console.error('Error setting item values:', error, item);
      }
    }
  }, [item]);

  const updateMutation = useMutation(
    () => {
      if (!item) return Promise.reject('No item');
      return collectionsApi.updateCollectionItem(item.id, {
        statuses: selectedFlags,
        rating: rating > 0 ? rating : undefined,
        notes: notes || undefined,
        watched_at: watchedAt || undefined,
      });
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('myCollection');
        queryClient.invalidateQueries('collectionStats');
        onClose();
      },
      onError: (error: any) => {
        alert(error.response?.data?.detail || 'Failed to update collection item.');
      },
    }
  );

  if (!isOpen || !item || !item.media_details) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate();
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">Edit Collection Item</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Media Info */}
        <div className="p-6 border-b bg-gray-50">
          <div className="flex gap-4">
            <div className="w-20 h-28 bg-gray-200 rounded flex-shrink-0">
              {item.media_details.cover_image_url ? (
                <img
                  src={item.media_details.cover_image_url}
                  alt={item.media_details.title}
                  className="w-full h-full object-cover rounded"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-2xl">📚</div>
              )}
            </div>
            <div>
              <h3 className="font-semibold text-lg">{item.media_details.title}</h3>
              <p className="text-sm text-gray-600">{item.media_details.media_type.replace('_', ' ')}</p>
              <p className="text-sm text-gray-500">
                Added {new Date(item.added_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Property Flags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Properties <span className="text-red-500">*</span>
              <span className="text-sm font-normal text-gray-500 ml-2">
                (Select one or more)
              </span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {flagOptions.map((option) => {
                const isSelected = selectedFlags.includes(option.value);
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => {
                      if (isSelected) {
                        if (selectedFlags.length > 1) {
                          setSelectedFlags(selectedFlags.filter(f => f !== option.value));
                        }
                      } else {
                        setSelectedFlags([...selectedFlags, option.value]);
                      }
                    }}
                    className={`p-3 border-2 rounded-lg text-left transition-all relative ${
                      isSelected
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute top-2 right-2 w-5 h-5 bg-primary-500 text-white rounded-full flex items-center justify-center text-xs">
                        ✓
                      </div>
                    )}
                    <div className="font-medium">{option.label}</div>
                    <div className="text-sm text-gray-600">{option.description}</div>
                  </button>
                );
              })}
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Selected: {selectedFlags.length} propert{selectedFlags.length !== 1 ? 'ies' : 'y'}
            </p>
          </div>

          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rating (0-10)
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={rating}
                onChange={(e) => setRating(parseFloat(e.target.value))}
                className="flex-1"
              />
              <div className="flex items-center gap-1 min-w-[80px]">
                <Star className="w-5 h-5 text-yellow-500 fill-current" />
                <span className="font-semibold text-lg">{Number(rating).toFixed(1)}</span>
              </div>
            </div>
            {rating === 0 && (
              <p className="text-sm text-gray-500 mt-1">Move slider to add a rating</p>
            )}
          </div>

          {/* Watched Date */}
          {selectedFlags.includes('watched') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Watched/Read/Listened Date (optional)
              </label>
              <input
                type="date"
                value={watchedAt}
                onChange={(e) => setWatchedAt(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="input"
              />
            </div>
          )}

          {/* Lending Records Display */}
          {item.lending_records && item.lending_records.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lending History
              </label>
              <div className="space-y-2">
                {item.lending_records.map((record) => (
                  <div key={record.id} className="p-3 bg-gray-50 rounded border">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="font-medium">
                          {record.lending_type === 'lent' ? 'Lent to' : 'Borrowed from'}:{' '}
                        </span>
                        <span>{record.person_name}</span>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${
                        record.is_returned ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {record.is_returned ? 'Returned' : 'Active'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(record.lent_at).toLocaleDateString()}
                      {record.returned_at && ` - ${new Date(record.returned_at).toLocaleDateString()}`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Your thoughts, comments, or any details you want to remember..."
              rows={4}
              className="input resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={updateMutation.isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={updateMutation.isLoading || selectedFlags.length === 0}
            >
              {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
