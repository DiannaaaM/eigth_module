from django.contrib import admin
from .models import Course, Lesson


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

