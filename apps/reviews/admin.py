
# apps/reviews/admin.py
from django.contrib import admin
from .models import Review, ReviewHelpful

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['lab', 'user', 'rating', 'position', 'duration', 'created_at']
    list_filter = ['position', 'duration', 'rating', 'is_verified']
    search_fields = ['lab__name', 'user__email', 'review_text']
    readonly_fields = ['helpful_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Review Info', {
            'fields': ('lab', 'user', 'position', 'duration')
        }),
        ('Ratings', {
            'fields': ('rating', 'category_ratings')
        }),
        ('Content', {
            'fields': ('review_text', 'pros', 'cons')
        }),
        ('Metadata', {
            'fields': ('is_verified', 'helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )