# Performance Optimization Guide

## 1. Add Database Indexes (CRITICAL)

Run the `add_indexes.sql` file against your PostgreSQL database:

```bash
psql -U your_username -d your_database -f add_indexes.sql
```

This will create indexes on:
- tndr_pk columns (for faster filtering)
- DEPARTMENT_CODE, DISTRICT_CODE (for faster JOINs)
- PROJECT_NAME (for faster text searches)
- PHYSICAL_PROGRESS (for faster completion filtering)
- Composite indexes for common JOIN patterns

**Expected improvement: 5-10x faster queries**

## 2. Enable Redis Caching

Currently Redis is disabled. To enable it:

1. Install and start Redis server
2. Update `app/api/utils/redis_client.py` to restore the original connection logic
3. Restart your application

**Expected improvement: 100x faster for repeated requests**

## 3. Increase page_size limit (if needed)

If users need more data per page, consider increasing the max page_size from 100 to 500 in controllers.

## 4. Database Connection Pooling

The app already uses connection pooling. Ensure your `.env` has:
```
DB_MIN_CONNECTIONS=2
DB_MAX_CONNECTIONS=10
```

## 5. Monitor Slow Queries

Add this to PostgreSQL config to log slow queries:
```
log_min_duration_statement = 1000  # Log queries taking > 1 second
```

## Quick Wins (Do These First):
1. Run add_indexes.sql ✓
2. Enable Redis caching
3. Test performance

