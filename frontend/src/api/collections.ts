import apiClient from './client';
import type {
  UserMedia,
  UserMediaCollection,
  CollectionStats,
  PaginatedResponse,
  CollectionStatus,
  CollectionFlag,
  LendingRecord
} from '../types';

// NEW - for redesigned collection model
interface AddToCollectionData {
  media: string;
  statuses?: CollectionFlag[];
  rating?: number;
  notes?: string;
  is_owned?: boolean;
  is_wishlist?: boolean;
  is_watched?: boolean;
  is_in_progress?: boolean;
  watched_at?: string;
  lend_to?: string;
  borrow_from?: string;
}

interface UpdateCollectionData {
  statuses?: CollectionFlag[];
  rating?: number;
  notes?: string;
  is_owned?: boolean;
  is_wishlist?: boolean;
  is_watched?: boolean;
  is_in_progress?: boolean;
  watched_at?: string;
}

interface AddLendingRecordData {
  lending_type: 'lent' | 'borrowed';
  person_name: string;
  notes?: string;
}

interface UpdateLendingRecordData {
  returned_at?: string;
  is_returned?: boolean;
  notes?: string;
}

// DEPRECATED - old collection model
interface OldAddToCollectionData {
  media: string;
  status: CollectionStatus;
  rating?: number;
  notes?: string;
  completed_at?: string;
}

interface OldUpdateCollectionData {
  status?: CollectionStatus;
  rating?: number;
  notes?: string;
  completed_at?: string;
}

export const collectionsApi = {
  // Get user's collection (NEW - uses flag filter)
  getMyCollection: async (flag?: CollectionFlag, page = 1) => {
    const params: any = { page };
    if (flag) params.flag = flag;
    const response = await apiClient.get<PaginatedResponse<UserMediaCollection>>('/api/collections/my/', { params });
    return response.data;
  },

  // Add media to collection (NEW - uses statuses array)
  addToCollection: async (data: AddToCollectionData) => {
    const response = await apiClient.post<UserMediaCollection>('/api/collections/', data);
    return response.data;
  },

  // Update collection item (NEW - uses flag fields)
  updateCollectionItem: async (id: string, data: UpdateCollectionData) => {
    const response = await apiClient.patch<UserMediaCollection>(`/api/collections/${id}/`, data);
    return response.data;
  },

  // Remove from collection
  removeFromCollection: async (id: string) => {
    await apiClient.delete(`/api/collections/${id}/`);
  },

  // Get collection statistics (NEW - returns by_flags)
  getStats: async () => {
    const response = await apiClient.get<CollectionStats>('/api/collections/stats/');
    return response.data;
  },

  // Get collection timeline (NEW - returns UserMediaCollection)
  getTimeline: async (page = 1) => {
    const response = await apiClient.get<PaginatedResponse<UserMediaCollection>>('/api/collections/timeline/', {
      params: { page }
    });
    return response.data;
  },

  // NEW - Lending record endpoints
  getLendingRecords: async (collectionId: string) => {
    const response = await apiClient.get<LendingRecord[]>(`/api/collections/${collectionId}/lending/`);
    return response.data;
  },

  addLendingRecord: async (collectionId: string, data: AddLendingRecordData) => {
    const response = await apiClient.post<LendingRecord>(`/api/collections/${collectionId}/lending/`, data);
    return response.data;
  },

  updateLendingRecord: async (lendingId: string, data: UpdateLendingRecordData) => {
    const response = await apiClient.patch<LendingRecord>(`/api/collections/lending/${lendingId}/`, data);
    return response.data;
  },

  deleteLendingRecord: async (lendingId: string) => {
    await apiClient.delete(`/api/collections/lending/${lendingId}/`);
  },
};
