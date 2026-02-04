# YourMedia Frontend

React + TypeScript + Vite frontend for Your Media Collection.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## Features

✅ **Browse Media** - Browse books, music, movies with advanced filters
✅ **Timeline View** - See media organized by release date
✅ **Collection Management** - Add, rate, and track your personal collection
✅ **Advanced Filtering** - Filter by author, artist, director, actor, genre, year
✅ **Authentication** - JWT-based login and registration
✅ **Responsive Design** - Works on desktop and mobile

## Pages

- `/` - Home page with stats and recent media
- `/media` - Browse all media with filters
- `/media/:id` - Media detail page
- `/timeline` - Release timeline view
- `/collection` - Your personal collection (requires login)
- `/login` - Login page
- `/register` - Registration page

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## API Integration

The frontend proxies API requests to the Django backend at `http://localhost:8000`.

Make sure the backend is running before starting the frontend.

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── api/              # API client and endpoints
├── components/       # Reusable components
├── pages/           # Page components
├── types/           # TypeScript types
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```
