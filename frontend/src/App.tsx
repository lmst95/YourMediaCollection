import { Routes, Route, Navigate } from 'react-router-dom';
import { authApi } from './api/auth';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import MediaListPage from './pages/MediaListPage';
import MediaDetailPage from './pages/MediaDetailPage';
import TimelinePage from './pages/TimelinePage';
import CollectionPageGrouped from './pages/CollectionPageGrouped';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ErrorBoundary from './components/ErrorBoundary';

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!authApi.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <ErrorBoundary>
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/media" element={<MediaListPage />} />
        <Route path="/media/:id" element={<MediaDetailPage />} />
        <Route path="/timeline" element={<TimelinePage />} />
        <Route
          path="/collection"
          element={
            <ProtectedRoute>
              <CollectionPageGrouped />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
    </ErrorBoundary>
  );
}

export default App;
