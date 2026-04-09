from django.contrib import admin
from .models import Course, Lesson

# Register your models here.

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'get_lessons_count')
    list_filter = ('owner',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    get_lessons_count.short_description = 'Количество уроков'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner')
    list_filter = ('course', 'owner')
    search_fields = ('title', 'description')