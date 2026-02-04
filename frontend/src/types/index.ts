// API Types for Your Media Collection

export type MediaType = 'movie' | 'tv_series' | 'book' | 'music' | 'concert' | 'document';

// DEPRECATED - old single status model
export type CollectionStatus =
  | 'owned'
  | 'watched'
  | 'read'
  | 'listened'
  | 'wishlist'
  | 'borrowed'
  | 'lent'
  | 'in_progress';

// NEW - property flags for redesigned collection model
export type CollectionFlag = 'owned' | 'wishlist' | 'watched' | 'in_progress';

export interface Media {
  id: string;
  media_type: MediaType;
  title: string;
  description: string;
  release_date: string | null;
  cover_image_url: string;
  genres: string[];
  external_ids: Record<string, any>;
  metadata: Record<string, any>;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface MovieDetails extends Media {
  movie: {
    runtime_minutes: number | null;
    director: string;
    cast: Array<{ name: string; character: string }>;
    tmdb_id: number | null;
    imdb_id: string;
  };
}

export interface BookDetails extends Media {
  book: {
    authors: string[];
    isbn: string | null;
    publisher: string;
    page_count: number | null;
    language: string;
    openlibrary_id: string | null;
  };
}

export interface MusicDetails extends Media {
  music: {
    artists: string[];
    album_type: 'album' | 'single' | 'compilation' | 'ep';
    track_count: number | null;
    duration_seconds: number | null;
    label: string;
    musicbrainz_id: string | null;
  };
}

// Lending record for new collection model
export interface LendingRecord {
  id: string;
  lending_type: 'lent' | 'borrowed';
  person_name: string;
  notes: string;
  lent_at: string;
  returned_at: string | null;
  is_returned: boolean;
}

// NEW - redesigned collection model (one per user per media)
export interface UserMediaCollection {
  id: string;
  user: string;
  user_username: string;
  media: string;
  media_details: Media;
  rating: number | null;
  notes: string;
  is_owned: boolean;
  is_wishlist: boolean;
  is_watched: boolean;
  is_in_progress: boolean;
  status_flags: CollectionFlag[];
  added_at: string;
  watched_at: string | null;
  updated_at: string;
  lending_records: LendingRecord[];
  active_lent_to: string[];
  active_borrowed_from: string[];
}

// DEPRECATED - old collection model (multiple entries per media)
export interface UserMedia {
  id: string;
  user: string;
  user_username: string;
  media: string;
  media_details: Media;
  status: CollectionStatus;
  status_display: string;
  rating: number | null;
  notes: string | null;
  added_at: string;
  completed_at: string | null;
  updated_at: string;
}

export interface CollectionStats {
  total_items: number;
  by_type: Record<string, number>;
  by_flags: Record<string, number>;
  average_rating: number | null;
  total_owned: number;
  total_wishlist: number;
  total_watched: number;
  total_in_progress: number;
  // DEPRECATED - old field
  by_status?: Record<string, number>;
}

export interface User {
  id: string;
  username: string;
  email: string;
  display_name: string;
  bio: string;
  avatar_url: string;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Filter types
export interface MediaFilters {
  media_type?: MediaType;
  genre?: string;
  release_year?: number;
  release_year_min?: number;
  release_year_max?: number;
  title_contains?: string;
  author?: string;
  artist?: string;
  director?: string;
  actor?: string;
  creator?: string;
  contributor?: string;
  search?: string;
  ordering?: string;
}
