# apps/utils/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .cache import CacheManager, invalidate_model_cache


@receiver(post_save, sender='universities.University')
@receiver(post_delete, sender='universities.University')
def invalidate_university_cache(sender, instance, **kwargs):
    """Invalidate university-related caches when University changes"""
    CacheManager.invalidate_related_caches('university', instance.id)
    print(f"Invalidated university cache for: {instance.name}")


@receiver(post_save, sender='universities.Department')
@receiver(post_delete, sender='universities.Department')
def invalidate_department_cache(sender, instance, **kwargs):
    """Invalidate department-related caches when Department changes"""
    CacheManager.invalidate_related_caches('department', instance.id)
    print(f"Invalidated department cache for: {instance.name}")


@receiver(post_save, sender='universities.UniversityDepartment')
@receiver(post_delete, sender='universities.UniversityDepartment')
def invalidate_university_department_cache(sender, instance, **kwargs):
    """Invalidate university department caches when UniversityDepartment changes"""
    CacheManager.invalidate_related_caches('department')
    # Also invalidate specific university's department cache
    if hasattr(instance, 'university_id'):
        cache_key = f"insidelab:1:DEPARTMENTS:university:{instance.university_id}"
        cache.delete(cache_key)
    print(f"Invalidated university department cache for: {instance}")


@receiver(post_save, sender='universities.Professor')
@receiver(post_delete, sender='universities.Professor')
def invalidate_professor_cache(sender, instance, **kwargs):
    """Invalidate professor-related caches when Professor changes"""
    CacheManager.invalidate_related_caches('professor', instance.id)
    print(f"Invalidated professor cache for: {instance.name}")


@receiver(post_save, sender='labs.Lab')
@receiver(post_delete, sender='labs.Lab')
def invalidate_lab_cache(sender, instance, **kwargs):
    """Invalidate lab-related caches when Lab changes"""
    CacheManager.invalidate_related_caches('lab', instance.id)
    print(f"Invalidated lab cache for: {instance.name}")


@receiver(post_save, sender='reviews.Review')
@receiver(post_delete, sender='reviews.Review')
def invalidate_review_cache(sender, instance, **kwargs):
    """Invalidate review-related caches when Review changes"""
    CacheManager.invalidate_related_caches('review', instance.id)
    # Also invalidate the related lab's cache since ratings may have changed
    if hasattr(instance, 'lab_id'):
        CacheManager.invalidate_related_caches('lab', instance.lab_id)
    print(f"Invalidated review cache for review: {instance.id}")


@receiver(post_save, sender='universities.ResearchGroup')
@receiver(post_delete, sender='universities.ResearchGroup')
def invalidate_research_group_cache(sender, instance, **kwargs):
    """Invalidate research group caches when ResearchGroup changes"""
    CacheManager.invalidate_related_caches('research_group', instance.id)
    print(f"Invalidated research group cache for: {instance.name}")


@receiver(post_save, sender='authentication.User')
def invalidate_user_cache(sender, instance, **kwargs):
    """Invalidate user-specific caches when User changes"""
    # Invalidate user profile cache
    cache_key = f"insidelab:1:USER_PROFILE:{instance.id}"
    cache.delete(cache_key)
    print(f"Invalidated user cache for: {instance.email}")


# Bulk cache invalidation for admin actions
def invalidate_all_caches():
    """Invalidate all application caches - use sparingly"""
    cache.clear()
    print("All caches cleared!")


def warm_critical_caches():
    """Warm up critical caches after invalidation"""
    from .cache import warm_cache
    warm_cache()
    print("Critical caches warmed up!")