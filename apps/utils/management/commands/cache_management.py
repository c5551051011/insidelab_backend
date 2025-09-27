# apps/utils/management/commands/cache_management.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.utils.cache import warm_cache, CacheManager
from apps.utils.signals import invalidate_all_caches, warm_critical_caches


class Command(BaseCommand):
    help = 'Manage application caches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            help='Action to perform: warm, clear, status, or warmcritical',
            choices=['warm', 'clear', 'status', 'warmcritical'],
            required=True
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'warm':
            self.stdout.write('Warming up caches...')
            warm_cache()
            self.stdout.write(self.style.SUCCESS('✅ Cache warming completed'))

        elif action == 'clear':
            self.stdout.write('Clearing all caches...')
            invalidate_all_caches()
            self.stdout.write(self.style.SUCCESS('✅ All caches cleared'))

        elif action == 'warmcritical':
            self.stdout.write('Warming critical caches...')
            warm_critical_caches()
            self.stdout.write(self.style.SUCCESS('✅ Critical caches warmed'))

        elif action == 'status':
            self.stdout.write('Cache Status:')
            try:
                # Test Redis connection
                cache.set('test_key', 'test_value', 10)
                test_value = cache.get('test_key')
                if test_value == 'test_value':
                    self.stdout.write(self.style.SUCCESS('✅ Redis cache connection: OK'))
                    cache.delete('test_key')
                else:
                    self.stdout.write(self.style.ERROR('❌ Redis cache connection: FAILED'))

                # Check cache stats (if available)
                from django_redis import get_redis_connection
                redis_conn = get_redis_connection("default")
                info = redis_conn.info()

                self.stdout.write(f"📊 Cache Statistics:")
                self.stdout.write(f"   Connected clients: {info.get('connected_clients', 'N/A')}")
                self.stdout.write(f"   Used memory: {info.get('used_memory_human', 'N/A')}")
                self.stdout.write(f"   Cache hits: {info.get('keyspace_hits', 'N/A')}")
                self.stdout.write(f"   Cache misses: {info.get('keyspace_misses', 'N/A')}")

                # Count keys by pattern
                patterns = ['UNIVERSITIES*', 'DEPARTMENTS*', 'LABS*', 'PROFESSORS*', 'REVIEWS*']
                for pattern in patterns:
                    keys = redis_conn.keys(f"insidelab:1:{pattern}")
                    self.stdout.write(f"   {pattern}: {len(keys)} keys")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Cache status check failed: {e}'))