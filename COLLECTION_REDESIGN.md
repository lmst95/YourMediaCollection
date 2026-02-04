# Collection System Redesign

## Problem with Old Design

The previous design created **separate database entries** for each status:
- If you marked a book as "Owned" + "Wishlist" + "Read", it created **3 separate rows**
- Same media appeared multiple times in collection
- Poor performance with many statuses
- Confusing data model
- Difficult to query and maintain

## New Improved Design

### One Entry Per Media
- **ONE UserMediaCollection entry** per user per media
- Multiple properties as **boolean flags** on the same entry
- Much cleaner, faster, and more intuitive

### Model Structure

#### UserMediaCollection (Main Model)
```python
class UserMediaCollection:
    user              # ForeignKey to User
    media             # ForeignKey to Media

    # Property flags (can have multiple)
    is_owned          # Boolean: user owns this
    is_wishlist       # Boolean: on wishlist
    is_watched        # Boolean: watched/read/listened
    is_in_progress    # Boolean: currently consuming

    # Metadata
    rating            # 0-10 rating
    notes             # User's notes
    added_at          # When added to collection
    watched_at        # When finished

    # UNIQUE CONSTRAINT: (user, media) - only ONE per user/media
```

#### LendingRecord (Separate Model)
```python
class LendingRecord:
    collection_item   # ForeignKey to UserMediaCollection
    lending_type      # 'lent' or 'borrowed'
    person_name       # Who you lent to/borrowed from
    lent_at           # When lent/borrowed
    returned_at       # When returned (null if still out)
    is_returned       # Boolean flag
```

## Benefits

### 1. **Performance**
- No duplicate entries
- Faster queries (single row lookup)
- Better indexing
- Less storage

### 2. **Data Integrity**
- One source of truth per media
- Rating/notes apply to the media, not to each status
- Cleaner data model

### 3. **Flexibility**
- Easy to add new properties
- Can have multiple flags simultaneously
- Lending tracked separately with full history

### 4. **Better UX**
- One card per media in UI
- All properties shown together
- Easier to understand and manage

## API Changes

### Old API (Deprecated)
```json
POST /api/collections/
{
  "media": "uuid",
  "status": "owned",
  "rating": 8.5
}
// This created ONE entry with status="owned"
// To add "wishlist" you had to POST again, creating a SECOND entry
```

### New API
```json
POST /api/collections/
{
  "media": "uuid",
  "statuses": ["owned", "wishlist", "watched"],
  "rating": 8.5,
  "notes": "Great book!",
  "lend_to": "John"  // Optional
}
// Creates ONE entry with all flags set
```

### Response Format
```json
{
  "id": "uuid",
  "media_details": { ... },
  "is_owned": true,
  "is_wishlist": true,
  "is_watched": true,
  "is_in_progress": false,
  "status_flags": ["owned", "wishlist", "watched"],
  "rating": 8.5,
  "notes": "Great book!",
  "active_lent_to": ["John"],
  "active_borrowed_from": [],
  "lending_records": [
    {
      "lending_type": "lent",
      "person_name": "John",
      "is_returned": false,
      "lent_at": "2025-01-17T..."
    }
  ]
}
```

## Migration Plan

1. **Create new tables** (UserMediaCollection, LendingRecord)
2. **Migrate existing data**:
   - Group old entries by (user, media)
   - Merge into single new entry with appropriate flags
   - Extract lending info to LendingRecord
3. **Update views and serializers**
4. **Update frontend**
5. **Test thoroughly**
6. **Drop old table** (after verification)

## Frontend Changes Needed

### Collection Display
- Show one card per media
- Display all active flags as badges
- Edit modal updates all flags at once
- Add lending management UI

### Example UI
```
┌─────────────────────────────────────┐
│ 📚 The Great Gatsby                 │
│ ⭐ 9.0/10                           │
│                                     │
│ [Owned] [Wishlist] [Read]          │  ← Multiple flags
│                                     │
│ Lent to: John (Active)              │  ← Lending info
│                                     │
│ Notes: Amazing classic novel...     │
│                                     │
│ Added: Jan 15, 2025                 │
│ [Edit] [Delete]                     │
└─────────────────────────────────────┘
```

## Database Schema

### Old Schema (Inefficient)
```
collections_usermedia
  id | user | media | status    | rating
  1  | u1   | m1    | owned     | 8.5
  2  | u1   | m1    | wishlist  | 8.5   ← Duplicate!
  3  | u1   | m1    | read      | 8.5   ← Duplicate!
```

### New Schema (Efficient)
```
collections_usermedia_v2
  id | user | media | is_owned | is_wishlist | is_watched | rating
  1  | u1   | m1    | true     | true        | true       | 8.5  ← One row!

collections_lending_record
  id | collection_item | lending_type | person_name | is_returned
  1  | 1               | lent         | John        | false
```

## Performance Comparison

### Old Design
- 1 book with 4 statuses = **4 database rows**
- 100 books with avg 3 statuses = **300 rows**
- Query: JOIN + WHERE status IN (...)

### New Design
- 1 book with 4 statuses = **1 database row**
- 100 books = **100 rows** (3x less!)
- Query: Simple WHERE with boolean columns (faster)

## Notes

- Old UserMedia model kept for backward compatibility during migration
- Will be removed after successful migration
- New design is more aligned with how users think about their collection
- Easier to add features like "favorite", "currently reading", etc.
