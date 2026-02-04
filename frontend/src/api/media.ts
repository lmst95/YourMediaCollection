import apiClient from './client';
import type { Media, PaginatedResponse, MediaFilters } from '../types';

export const mediaApi = {
  // Get all media with filters
  getMedia: async (filters?: MediaFilters, page = 1) => {
    const params = { ...filters, page };
    const response = await apiClient.get<PaginatedResponse<Media>>('/api/media/', { params });
    return response.data;
  },

  // Get media by ID
  getMediaById: async (id: string) => {
    const response = await apiClient.get<Media>(`/api/media/${id}/`);
    return response.data;
  },

  // Get media timeline
  getTimeline: async (filters?: MediaFilters, page = 1) => {
    const params = { ...filters, page };
    const response = await apiClient.get<PaginatedResponse<Media>>('/api/media/timeline/', { params });
    return response.data;
  },

  // Get movies
  getMovies: async (filters?: MediaFilters, page = 1) => {
    const params = { ...filters, page };
    const response = await apiClient.get<PaginatedResponse<Media>>('/api/media/movies/', { params });
    return response.data;
  },

  // Get TV series
  getTVSeries: async (filters?: MediaFilters, page = 1) => {
    const params = { ...filters, page };
    const response = await apiClient.get<PaginatedResponse<Media>>('/api/media/tv-series/', { params });
    return response.data;
  },

  // Get books
  getBooks: async (filters?: MediaFilters, page = 1) => {
    const params = { ...filters, page };
    const response = await apiClient.get<PaginatedResponse<Media>>('/api/media/books/', { params });
    return response.data;
  },

  // Get music
  getMusic: async (filters?: MediaFilters, page = 1) => {
    const params = { ...filters, page };
    const response = await apiClient.get<PaginatedResponse<Media>>('/api/media/music/', { params });
    return response.data;
  },

  // Get genres
  getGenres: async () => {
    const response = await apiClient.get<{ genres: string[] }>('/api/media/genres/');
    return response.data.genres;
  },
};
