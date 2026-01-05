from django.contrib import admin
from .models import (
    Category, Course, Module, Lesson, 
    Quiz, Question, Answer, Project, 
    Enrollment, LessonProgress, QuizAttempt, 
    ProjectSubmission, Certificate
)

# --- 1. INLINES ---
# Memungkinkan edit data terkait di halaman yang sama

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4 # Default menampilkan 4 pilihan jawaban
    min_num = 2 # Minimal harus ada 2 pilihan

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order', 'duration_minutes')

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    show_change_link = True

# --- 2. MODEL ADMINS ---

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'level', 'price', 'is_published')
    list_filter = ('category', 'level', 'is_published')
    search_fields = ('title', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)} # Otomatis isi slug saat ketik judul
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    inlines = [LessonInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'passing_score')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    inlines = [AnswerInline]

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'status', 'grade')
    list_filter = ('status',)
    list_editable = ('status', 'grade') # Bisa edit nilai langsung dari list
    search_fields = ('user__username', 'project__title')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'user', 'course', 'issued_at')
    readonly_fields = ('certificate_number', 'issued_at') # Tidak bisa diubah manual
    search_fields = ('certificate_number', 'user__username')

# --- 3. REGISTER SISANYA ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
admin.site.register(QuizAttempt)
admin.site.register(Project)