from django.contrib import admin
# Seven imported classes required (Course, Lesson, Instructor, Learner, Question, Choice, Submission)
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# Choice Inline allows adding choices right inside the Question view
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4

# Question Inline allows editing questions directly inside the Course page view
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

# Custom Admin representation for Question
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text', 'course', 'grade']

# Custom Admin representation for Lesson
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']

# Custom Admin representation for Course (includes items and lessons inline view)
class CourseAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

# Registering models on Django Site Portal
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Instructor)
admin.site.register(Learner)
