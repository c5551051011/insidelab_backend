# apps/sessions/admin.py
from django.contrib import admin
from .models import MockInterviewSession, SessionLab, SessionTimeSlot


class SessionLabInline(admin.TabularInline):
    model = SessionLab
    extra = 0
    readonly_fields = ('created_at',)


class SessionTimeSlotInline(admin.TabularInline):
    model = SessionTimeSlot
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(MockInterviewSession)
class MockInterviewSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'session_type', 'status', 'match_type',
        'interviewer', 'confirmed_date', 'confirmed_time',
        'total_price', 'created_at'
    )
    list_filter = ('status', 'session_type', 'match_type', 'created_at')
    search_fields = ('user__email', 'interviewer__email', 'focus_areas')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SessionLabInline, SessionTimeSlotInline]

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Session Details', {
            'fields': ('session_type', 'focus_areas', 'additional_notes', 'total_price')
        }),
        ('Status & Matching', {
            'fields': ('status', 'match_type', 'interviewer')
        }),
        ('Schedule', {
            'fields': ('confirmed_date', 'confirmed_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'interviewer'
        ).prefetch_related('target_labs', 'preferred_slots')


@admin.register(SessionLab)
class SessionLabAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'lab', 'priority', 'created_at')
    list_filter = ('priority', 'created_at')
    search_fields = ('session__user__email', 'lab__name')
    readonly_fields = ('created_at',)


@admin.register(SessionTimeSlot)
class SessionTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'date', 'time', 'priority', 'created_at')
    list_filter = ('priority', 'date', 'created_at')
    search_fields = ('session__user__email',)
    readonly_fields = ('created_at',)
