# Frontend Migration Complete

## Overview
The frontend has been successfully updated to work with the new collection model that uses boolean flags instead of single status values.

## Changes Made

### 1. Type Definitions (`frontend/src/types/index.ts`)
- Added `CollectionFlag` type for the new property flags: `'owned' | 'wishlist' | 'watched' | 'in_progress'`
- Added `LendingRecord` interface for tracking lending/borrowing
- Added `UserMediaCollection` interface (new model)
- Kept old `UserMedia` interface for backward compatibility (marked as deprecated)
- Updated `CollectionStats` to include `by_flags` and individual flag counts

### 2. API Client (`frontend/src/api/collections.ts`)
- Updated all API functions to use `UserMediaCollection` instead of `UserMedia`
- Changed `getMyCollection` to accept `CollectionFlag` instead of `CollectionStatus`
- Updated `addToCollection` to accept `statuses` array and lending fields
- Updated `updateCollectionItem` to work with flag-based updates
- Added new lending record endpoints:
  - `getLendingRecords(collectionId)`
  - `addLendingRecord(collectionId, data)`
  - `updateLendingRecord(lendingId, data)`
  - `deleteLendingRecord(lendingId)`

### 3. Add to Collection Modal (`frontend/src/components/AddToCollectionModal.tsx`)
**Complete rewrite** to support new model:
- Changed from 8 status options to 4 flag options
- Users can now select multiple properties simultaneously
- Simplified the form (no more separate forms for each status)
- Added `lend_to` and `borrow_from` fields that create lending records
- Changed `completed_at` to `watched_at`
- Single API call creates one collection item with all flags

### 4. Edit Collection Modal (`frontend/src/components/EditCollectionModal.tsx`)
**Complete rewrite** to support new model:
- Now works with `UserMediaCollection` type
- Shows multiple property flags as toggleable buttons
- Displays lending history if available
- Updates all flags in a single API call
- Added visual indicators for lending records (active/returned status)

### 5. Collection Page (`frontend/src/pages/CollectionPage.tsx`)
**Major updates**:
- Changed filter from status dropdown to flag dropdown
- Updated stats display to show individual flag counts
- Each collection item now displays multiple flag badges with colors:
  - Owned: Blue
  - Wishlist: Yellow
  - Watched: Green
  - In Progress: Purple
- Added lending info display (who item is lent to/borrowed from)
- Updated to work with `UserMediaCollection` type

### 6. Collection Timeline (`frontend/src/components/CollectionTimeline.tsx`)
**Updated**:
- Changed to use `UserMediaCollection` type
- Timeline dots now use the first flag's color
- Displays all property flags as badges
- Updated to work with new data structure

## Key Differences from Old Model

### Old Model (Multiple Rows)
```typescript
// Book with 3 statuses = 3 database rows
[
  { media: 'book123', status: 'owned', rating: 8.5 },
  { media: 'book123', status: 'wishlist', rating: 8.5 },
  { media: 'book123', status: 'read', rating: 8.5 },
]
```

### New Model (Single Row)
```typescript
// Book with 3 properties = 1 database row
{
  media: 'book123',
  is_owned: true,
  is_wishlist: true,
  is_watched: true,
  is_in_progress: false,
  status_flags: ['owned', 'wishlist', 'watched'],
  rating: 8.5,
  lending_records: [...]
}
```

## API Changes

### Old API
```javascript
// Had to make 3 separate API calls
POST /api/collections/ { media: 'id', status: 'owned' }
POST /api/collections/ { media: 'id', status: 'wishlist' }
POST /api/collections/ { media: 'id', status: 'read' }

// Filter by status
GET /api/collections/my/?status=owned
```

### New API
```javascript
// Single API call with multiple flags
POST /api/collections/ {
  media: 'id',
  statuses: ['owned', 'wishlist', 'watched'],
  rating: 8.5,
  lend_to: 'John'  // Optional
}

// Filter by flag
GET /api/collections/my/?flag=owned
```

## Benefits

1. **Performance**: 3x fewer database rows
2. **Simpler UX**: One card per media item with all properties visible
3. **Better Data Model**: Rating and notes apply to the media, not each status
4. **Lending Tracking**: Proper history with who/when for lent/borrowed items
5. **Atomic Updates**: Change multiple properties in one operation

## Testing Checklist

- [ ] Add new item to collection with multiple flags
- [ ] Edit existing item and change flags
- [ ] View collection with flag filter
- [ ] Check collection statistics
- [ ] View collection timeline
- [ ] Add lending record when adding to collection
- [ ] View lending history in edit modal
- [ ] Remove item from collection

## Notes

- Old `UserMedia` types are kept for backward compatibility but marked as deprecated
- The backend supports both old and new serializers during migration
- Frontend now exclusively uses the new model
- All UI components have been updated to display multiple flags
