# Migration Steps for Collection Redesign

## Current Status

The new models (`UserMediaCollection` and `LendingRecord`) have been created, but the views still reference the old `UserMedia` model. We need to update the entire stack.

## Step-by-Step Migration

### 1. Temporarily Disable Collection URLs (to allow migrations)

Edit `apps/collections/views.py` to import the new models:

```python
# Change this:
from apps.collections.models import UserMedia, CollectionStatus

# To this:
from apps.collections.models import UserMediaCollection, LendingRecord
```

### 2. Run Migrations

```bash
python manage.py makemigrations collections
python manage.py migrate collections
```

This will create the new tables:
- `collections_usermedia_v2`
- `collections_lending_record`

### 3. Migrate Data (Optional - if you have existing data)

Create a data migration to move data from old to new structure:

```bash
python manage.py makemigrations collections --empty --name migrate_to_new_structure
```

Then edit the migration file to consolidate old entries.

### 4. Update Views

The views need complete rewriting because the API has changed:
- No more `status` field
- Now uses boolean flags: `is_owned`, `is_wishlist`, etc.
- Filtering works differently
- Stats calculation changes

### 5. Update Frontend

Frontend changes needed:
- Update TypeScript types
- Change API calls to use new structure
- Update UI to show multiple flags per item

## Quick Fix to Get Migrations Working

To get migrations working immediately, we can temporarily comment out the views or create stub implementations.

Would you like me to:
A) Create stub views that make migrations work (then update properly later)
B) Completely rewrite all views now to match the new structure
C) Create a migration path that keeps both old and new systems working simultaneously

## Recommendation

I recommend option **C** - dual system during transition:
1. Keep old `UserMedia` model and views working
2. Add new `UserMediaCollection` views alongside
3. Migrate data gradually
4. Update frontend to use new endpoints
5. Remove old system once verified

This allows zero-downtime migration.
