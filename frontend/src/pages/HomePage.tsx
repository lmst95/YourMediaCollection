import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Film, Book, Music, Clock, TrendingUp } from 'lucide-react';
import { mediaApi } from '../api/media';
import { collectionsApi } from '../api/collections';
import { authApi } from '../api/auth';
import MediaCard from '../components/MediaCard';

export default function HomePage() {
  const isAuthenticated = authApi.isAuthenticated();

  // Fetch recent media
  const { data: recentMedia } = useQuery('recentMedia', () =>
    mediaApi.getMedia({}, 1)
  );

  // Fetch collection stats if authenticated
  const { data: stats } = useQuery(
    'collectionStats',
    () => collectionsApi.getStats(),
    { enabled: isAuthenticated }
  );

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-primary-500 to-primary-700 rounded-2xl text-white -mx-4 px-4">
        <h1 className="text-5xl font-bold mb-4">Your Media Collection</h1>
        <p className="text-xl mb-8 text-primary-100">
          Track, organize, and discover your favorite movies, books, music, and more
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/media" className="btn bg-white text-primary-600 hover:bg-gray-100">
            Browse Catalog
          </Link>
          {!isAuthenticated && (
            <Link to="/register" className="btn bg-primary-800 text-white hover:bg-primary-900">
              Get Started
            </Link>
          )}
        </div>
      </section>

      {/* Stats Section (if authenticated) */}
      {isAuthenticated && stats && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Your Collection</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Total Items</span>
                <TrendingUp className="w-5 h-5 text-primary-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.total_items}</p>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Movies</span>
                <Film className="w-5 h-5 text-purple-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {stats.by_type?.movie || 0}
              </p>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Books</span>
                <Book className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {stats.by_type?.book || 0}
              </p>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Music</span>
                <Music className="w-5 h-5 text-pink-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                {stats.by_type?.music || 0}
              </p>
            </div>
          </div>

          <Link
            to="/collection"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mt-4"
          >
            View full collection →
          </Link>
        </section>
      )}

      {/* Quick Links */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Explore</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/media?media_type=movie" className="card p-6 hover:shadow-lg transition-shadow">
            <Film className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Movies</h3>
            <p className="text-gray-600">Browse our movie catalog</p>
          </Link>

          <Link to="/media?media_type=book" className="card p-6 hover:shadow-lg transition-shadow">
            <Book className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Books</h3>
            <p className="text-gray-600">Discover books to read</p>
          </Link>

          <Link to="/media?media_type=music" className="card p-6 hover:shadow-lg transition-shadow">
            <Music className="w-12 h-12 text-pink-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Music</h3>
            <p className="text-gray-600">Explore music albums</p>
          </Link>
        </div>
      </section>

      {/* Recent Additions */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Recently Added</h2>
          <Link to="/timeline" className="flex items-center text-primary-600 hover:text-primary-700">
            <Clock className="w-5 h-5 mr-1" />
            View Timeline
          </Link>
        </div>

        {recentMedia && recentMedia.results.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {recentMedia.results.slice(0, 10).map((media) => (
              <MediaCard key={media.id} media={media} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p>No media items yet. Start by browsing the catalog!</p>
          </div>
        )}
      </section>
    </div>
  );
}
