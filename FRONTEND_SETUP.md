# Frontend Setup Guide

## Prerequisites

You need to install Node.js first:

### Install Node.js

**Option 1: Download from nodejs.org**
1. Visit https://nodejs.org/
2. Download the LTS version (recommended)
3. Run the installer
4. Restart your terminal

**Option 2: Using Winget (Windows)**
```bash
winget install OpenJS.NodeJS.LTS
```

**Option 3: Using nvm (Node Version Manager)**
```bash
# Install nvm from https://github.com/coreybutler/nvm-windows
nvm install lts
nvm use lts
```

After installation, verify:
```bash
node --version
npm --version
```

## Setup Instructions

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- React 18 + TypeScript
- React Router for navigation
- Axios for API calls
- React Query for data fetching
- Zustand for state management
- Tailwind CSS for styling
- Lucide React for icons
- Vite as build tool

### 3. Create Environment File
Create a `.env` file in the `frontend` directory:

```bash
# Frontend/.env
VITE_API_URL=http://localhost:8000
```

### 4. Start Development Server
```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

The API proxy is configured to forward `/api/*` requests to `http://localhost:8000`

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and endpoint functions
│   │   ├── client.ts     # Axios instance with auth interceptor
│   │   ├── auth.ts       # Authentication API
│   │   ├── media.ts      # Media catalog API
│   │   └── collections.ts # Collection management API
│   ├── components/       # Reusable React components
│   │   ├── Layout.tsx    # Main layout with navigation
│   │   ├── MediaCard.tsx # Media item card
│   │   ├── FilterBar.tsx # Search and filter UI
│   │   └── ...
│   ├── pages/           # Page components (routes)
│   │   ├── HomePage.tsx
│   │   ├── MediaListPage.tsx
│   │   ├── MediaDetailPage.tsx
│   │   ├── TimelinePage.tsx
│   │   ├── CollectionPage.tsx
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   ├── hooks/           # Custom React hooks
│   ├── store/           # Zustand stores
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # App entry point
│   └── index.css        # Global styles (Tailwind)
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── postcss.config.js    # PostCSS configuration
```

## Features Implemented

### API Integration
- ✅ Axios client with JWT authentication
- ✅ Automatic token refresh on 401 errors
- ✅ Request/response interceptors
- ✅ TypeScript types for all API responses

### Routes
- `/` - Home page with featured media
- `/media` - Browse all media with filters
- `/media/:id` - Media detail page
- `/timeline` - Release timeline view
- `/collection` - User's personal collection (protected)
- `/login` - Login page
- `/register` - Registration page

### Planned Features
- [ ] Complete component implementations
- [ ] Media browsing with advanced filters
- [ ] Collection management (add, rate, notes)
- [ ] Search functionality
- [ ] User authentication UI
- [ ] Responsive design
- [ ] Dark mode support

## Next Steps

After installing Node.js and running `npm install`, you can:

1. **Continue building components**: I've created the basic structure, but components need full implementation
2. **Test API integration**: Make sure the backend is running at `localhost:8000`
3. **Customize styling**: Tailwind classes are configured and ready to use
4. **Add more features**: The architecture supports easy extension

## Development Commands

```bash
# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Notes

- The frontend is configured to proxy API requests to the Django backend
- JWT tokens are stored in localStorage
- React Query handles caching and background refetching
- Tailwind CSS provides utility-first styling
- TypeScript ensures type safety across the app

## Troubleshooting

### Port already in use
If port 3000 is in use, Vite will automatically try 3001, 3002, etc.

### CORS errors
Make sure `CORS_ALLOWED_ORIGINS` in Django settings includes `http://localhost:3000`

### API connection errors
1. Check that Django server is running at `localhost:8000`
2. Verify `.env` file has correct `VITE_API_URL`
3. Check browser console for detailed error messages
