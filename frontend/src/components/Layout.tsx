import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Home, Film, Clock, Library, LogOut, User } from 'lucide-react';
import { authApi } from '../api/auth';

export default function Layout() {
  const navigate = useNavigate();
  const isAuthenticated = authApi.isAuthenticated();

  const handleLogout = () => {
    authApi.logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <Library className="w-8 h-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">Your Media Collection</span>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center space-x-6">
              <Link
                to="/"
                className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors"
              >
                <Home className="w-5 h-5" />
                <span>Home</span>
              </Link>

              <Link
                to="/media"
                className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors"
              >
                <Film className="w-5 h-5" />
                <span>Browse</span>
              </Link>

              <Link
                to="/timeline"
                className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors"
              >
                <Clock className="w-5 h-5" />
                <span>Timeline</span>
              </Link>

              {isAuthenticated && (
                <Link
                  to="/collection"
                  className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors"
                >
                  <Library className="w-5 h-5" />
                  <span>My Collection</span>
                </Link>
              )}

              {/* Auth Actions */}
              <div className="flex items-center space-x-3 ml-6 pl-6 border-l">
                {isAuthenticated ? (
                  <>
                    <Link to="/profile" className="text-gray-700 hover:text-primary-600">
                      <User className="w-5 h-5" />
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 text-gray-700 hover:text-red-600 transition-colors"
                    >
                      <LogOut className="w-5 h-5" />
                      <span>Logout</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link to="/login" className="btn btn-secondary">
                      Login
                    </Link>
                    <Link to="/register" className="btn btn-primary">
                      Register
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>&copy; 2026 Your Media Collection. Built with Django + React.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
