# Caching Implementation

This document describes the comprehensive caching implementation for the InsideLab backend API.

## Overview

The caching system uses Redis as the backend to significantly improve API performance by caching frequently accessed data and reducing database queries.

## Architecture

### Components

1. **Redis Cache Backend**: Primary caching storage
2. **Cache Decorators**: Automated caching for API views
3. **Cache Manager**: Centralized cache operations
4. **Signal-based Invalidation**: Automatic cache cleanup when data changes
5. **Management Commands**: Manual cache operations

### Cache Timeouts

| Data Type | Timeout | Reason |
|-----------|---------|---------|
| Universities | 24 hours | Rarely changes |
| Departments | 12 hours | Occasional updates |
| Professors | 6 hours | Regular updates |
| Research Groups | 2 hours | Moderate changes |
| Labs | 30 minutes | Frequent updates |
| Reviews | 15 minutes | Real-time updates |
| User Profiles | 30 minutes | Session-based |
| Search Results | 10 minutes | Dynamic content |

## Configuration

### Settings (settings.py)

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'insidelab',
        'TIMEOUT': 300,  # Default 5 minutes
    }
}
```

### Environment Variables

```bash
REDIS_URL=redis://127.0.0.1:6379/1  # Local development
REDIS_URL=redis://user:pass@host:port/db  # Production
```

## Usage

### API View Caching

Views are automatically cached using decorators:

```python
@method_decorator(cache_page(60 * 30), name='list')  # 30 minutes
@method_decorator(cache_page(60 * 60), name='retrieve')  # 1 hour
class LabViewSet(viewsets.ModelViewSet):
    # ...

@cache_response('DEPARTMENTS')
@action(detail=True, methods=['get'])
def departments(self, request, pk=None):
    # ...
```

### Manual Cache Operations

```python
from apps.utils.cache import CacheManager

# Cache universities
CacheManager.set_universities(data)

# Get cached universities
cached_data = CacheManager.get_universities()

# Invalidate caches
CacheManager.invalidate_related_caches('university', university_id)
```

### Cache Keys

Cache keys follow the pattern:
```
insidelab:1:{CACHE_TYPE}:{operation}:{parameters_hash}
```

Examples:
- `insidelab:1:UNIVERSITIES:list:abc123`
- `insidelab:1:DEPARTMENTS:university:14:def456`
- `insidelab:1:LABS:list:featured:ghi789`

## Cache Invalidation

### Automatic Invalidation

Django signals automatically invalidate related caches when models change:

```python
@receiver(post_save, sender='universities.University')
def invalidate_university_cache(sender, instance, **kwargs):
    CacheManager.invalidate_related_caches('university', instance.id)
```

### Manual Invalidation

```bash
# Clear all caches
python manage.py cache_management --action clear

# Warm up caches
python manage.py cache_management --action warm

# Check cache status
python manage.py cache_management --action status
```

## Performance Impact

### Expected Improvements

- **Universities List**: 80-90% faster (24h cache)
- **Departments**: 70-85% faster (12h cache)
- **Labs List**: 60-75% faster (30min cache)
- **Search Results**: 50-70% faster (10min cache)

### Monitoring

Use the cache status command to monitor performance:

```bash
python manage.py cache_management --action status
```

Output includes:
- Cache connection status
- Memory usage
- Hit/miss ratios
- Key counts by type

## Production Deployment

### Redis Setup

1. **Railway**: Use Railway's Redis service
2. **External**: AWS ElastiCache, Google Cloud Memorystore, etc.

### Environment Variables

```bash
REDIS_URL=redis://redis-service:6379/1
```

### Cache Warming

Set up cache warming on deployment:

```bash
python manage.py cache_management --action warm
```

## Best Practices

### Do's

- ✅ Cache read-heavy operations
- ✅ Use appropriate timeout values
- ✅ Monitor cache hit ratios
- ✅ Warm critical caches after deployment
- ✅ Invalidate caches when data changes

### Don'ts

- ❌ Don't cache user-specific data in shared cache
- ❌ Don't use very long timeouts for frequently changing data
- ❌ Don't forget to handle cache misses gracefully
- ❌ Don't cache error responses

## Troubleshooting

### Common Issues

1. **Cache Miss**: Check if Redis is running and accessible
2. **Stale Data**: Verify cache invalidation signals are working
3. **Memory Issues**: Monitor Redis memory usage and adjust timeouts
4. **Performance**: Check cache hit ratios and optimize cache keys

### Debug Commands

```bash
# Check cache status
python manage.py cache_management --action status

# Clear problematic caches
python manage.py cache_management --action clear

# Re-warm caches
python manage.py cache_management --action warm
```

## API Endpoints with Caching

| Endpoint | Cache Duration | Cache Key Pattern |
|----------|----------------|-------------------|
| `GET /universities/` | 24 hours | `UNIVERSITIES:list:*` |
| `GET /universities/{id}/` | 12 hours | `UNIVERSITIES:detail:*` |
| `GET /universities/{id}/departments/` | 12 hours | `DEPARTMENTS:university:*` |
| `GET /labs/` | 30 minutes | `LABS:list:*` |
| `GET /labs/{id}/` | 1 hour | `LABS:detail:*` |
| `GET /labs/featured/` | 1 hour | `LABS:featured:*` |
| `GET /labs/recruiting/` | 15 minutes | `LABS:recruiting:*` |

## Testing

Run the caching test suite:

```bash
python test_caching.py
```

This tests:
- Basic cache functionality
- CacheManager operations
- API endpoint caching
- Performance improvements
- Cache invalidation

## Maintenance

### Regular Tasks

1. **Monitor Memory**: Check Redis memory usage weekly
2. **Analyze Hit Ratios**: Review cache effectiveness monthly
3. **Update Timeouts**: Adjust based on usage patterns
4. **Clean Orphaned Keys**: Remove unused cache patterns

### Cache Warming Schedule

Consider setting up automatic cache warming:
- After deployments
- During low-traffic periods
- After bulk data imports

This caching implementation provides significant performance improvements while maintaining data consistency and freshness.