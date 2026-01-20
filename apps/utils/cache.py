# apps/utils/cache.py
import hashlib
from django.core.cache import cache
from django.conf import settings
from django.utils.encoding import force_bytes
from functools import wraps
import json


def get_cache_key(prefix, *args, **kwargs):
    """Generate a cache key from prefix and parameters"""
    # Create a unique key from arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items()) if kwargs else None
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(force_bytes(key_string)).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_response(cache_type, timeout=None, vary_on_user=False):
    """
    Decorator to cache view responses

    Args:
        cache_type: Key from CACHE_TIMEOUTS settings
        timeout: Override default timeout (in seconds)
        vary_on_user: Include user ID in cache key
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Get timeout from settings or use provided
            cache_timeout = timeout or getattr(settings, 'CACHE_TIMEOUTS', {}).get(cache_type, 300)

            # Build cache key
            key_parts = [cache_type, request.method, request.path]

            # Add query parameters to cache key
            if request.GET:
                query_string = request.GET.urlencode()
                key_parts.append(query_string)

            # Add user ID if requested
            if vary_on_user and hasattr(request, 'user') and request.user.is_authenticated:
                key_parts.append(f"user_{request.user.id}")

            cache_key = get_cache_key(*key_parts)

            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                print(f"🎯 Cache HIT for key: {cache_key}")
                from rest_framework.response import Response
                return Response(cached_data)
            else:
                print(f"❌ Cache MISS for key: {cache_key}")

            # Get fresh response
            response = view_func(self, request, *args, **kwargs)

            # Cache successful responses (cache the data, not the Response object)
            if hasattr(response, 'status_code') and response.status_code == 200:
                try:
                    # Only cache the data, not the rendered response
                    if hasattr(response, 'data'):
                        cache.set(cache_key, response.data, cache_timeout)
                        print(f"✅ Cache SET for key: {cache_key}, timeout: {cache_timeout}s")
                    else:
                        print(f"❌ Response has no data attribute: {cache_key}")
                except Exception as e:
                    # If caching fails, just return the response without caching
                    print(f"❌ Cache SET failed for key: {cache_key}, error: {e}")
                    pass

            return response
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching a pattern"""
    # Check if we're using a cache backend that supports pattern invalidation
    cache_backend = settings.CACHES.get('default', {}).get('BACKEND', '')

    # Skip invalidation for dummy cache or unsupported backends
    if 'dummy' in cache_backend.lower():
        return 0

    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(f"insidelab:1:{pattern}*")
        if keys:
            redis_conn.delete(*keys)
            return len(keys)
        return 0
    except Exception as e:
        # Silently skip for unsupported backends (e.g., DummyCache in tests)
        if 'does not support this feature' not in str(e):
            print(f"Cache invalidation error: {e}")
        return 0


def invalidate_model_cache(model_name, obj_id=None):
    """Invalidate cache for a specific model"""
    patterns = [
        f"{model_name.upper()}",
        f"{model_name.lower()}_list",
        f"{model_name.lower()}_detail",
    ]

    if obj_id:
        patterns.append(f"{model_name.lower()}_{obj_id}")

    total_deleted = 0
    for pattern in patterns:
        total_deleted += invalidate_cache_pattern(pattern)

    return total_deleted


class CacheManager:
    """Centralized cache management"""

    @staticmethod
    def get_universities():
        """Get cached universities list"""
        cache_key = get_cache_key('UNIVERSITIES', 'list')
        return cache.get(cache_key)

    @staticmethod
    def set_universities(data, timeout=None):
        """Cache universities list"""
        cache_key = get_cache_key('UNIVERSITIES', 'list')
        cache_timeout = timeout or settings.CACHE_TIMEOUTS.get('UNIVERSITIES', 86400)
        cache.set(cache_key, data, cache_timeout)

    @staticmethod
    def get_university_departments(university_id):
        """Get cached departments for a university"""
        cache_key = get_cache_key('DEPARTMENTS', 'university', university_id)
        return cache.get(cache_key)

    @staticmethod
    def set_university_departments(university_id, data, timeout=None):
        """Cache departments for a university"""
        cache_key = get_cache_key('DEPARTMENTS', 'university', university_id)
        cache_timeout = timeout or settings.CACHE_TIMEOUTS.get('DEPARTMENTS', 43200)
        cache.set(cache_key, data, cache_timeout)

    @staticmethod
    def delete_university_departments(university_id):
        """Delete cached departments for a university"""
        cache_key = get_cache_key('DEPARTMENTS', 'university', university_id)
        cache.delete(cache_key)

    @staticmethod
    def get_labs(filters=None):
        """Get cached labs list"""
        cache_key = get_cache_key('LABS', 'list', filters or {})
        return cache.get(cache_key)

    @staticmethod
    def set_labs(data, filters=None, timeout=None):
        """Cache labs list"""
        cache_key = get_cache_key('LABS', 'list', filters or {})
        cache_timeout = timeout or settings.CACHE_TIMEOUTS.get('LABS', 1800)
        cache.set(cache_key, data, cache_timeout)

    @staticmethod
    def invalidate_related_caches(model_name, obj_id=None):
        """Invalidate all related caches when data changes"""
        if model_name.lower() == 'university':
            invalidate_cache_pattern('UNIVERSITIES')
            invalidate_cache_pattern('DEPARTMENTS')
            invalidate_cache_pattern('PROFESSORS')
            invalidate_cache_pattern('LABS')

        elif model_name.lower() == 'department':
            invalidate_cache_pattern('DEPARTMENTS')
            invalidate_cache_pattern('PROFESSORS')
            invalidate_cache_pattern('LABS')

        elif model_name.lower() == 'lab':
            invalidate_cache_pattern('LABS')
            invalidate_cache_pattern('REVIEWS')

        elif model_name.lower() == 'professor':
            invalidate_cache_pattern('PROFESSORS')
            invalidate_cache_pattern('LABS')

        elif model_name.lower() == 'review':
            invalidate_cache_pattern('REVIEWS')
            invalidate_cache_pattern('LABS')  # Labs cache includes ratings


# Cache warming functions
def warm_cache():
    """Warm up frequently accessed cache entries"""
    from apps.universities.models import University
    from apps.labs.models import Lab

    # Warm university cache
    universities = list(University.objects.values('id', 'name', 'country', 'city'))
    CacheManager.set_universities(universities)

    # Warm popular labs cache
    popular_labs = list(Lab.objects.filter(
        overall_rating__gte=4.0
    ).values('id', 'name', 'overall_rating', 'review_count')[:50])
    CacheManager.set_labs(popular_labs, {'popular': True})

    print(f"Cache warmed: {len(universities)} universities, {len(popular_labs)} popular labs")