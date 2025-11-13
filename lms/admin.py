from django.contrib import admin
from .models import Course, Lesson, CourseSubscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'description')
    list_filter = ('title', 'owner')
    search_fields = ('title', 'description')
    raw_id_fields = ('owner',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner', 'video_link')
    list_filter = ('course', 'owner')
    search_fields = ('title', 'description')
    raw_id_fields = ('course', 'owner')


@admin.register(CourseSubscription)
class CourseSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('course', 'user')
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')

