from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import *

# --- 1. View untuk Me-render Halaman (HTML) ---
# @login_required
def category_page(request):
    return render(request, 'courses/category_list.html')

def api_category_list(request):
    """Mengambil semua kategori untuk ditampilkan di tabel"""
    categories = Category.objects.all().order_by('-id')
    data = [
        {
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'icon': cat.icon
        } for cat in categories
    ]
    return JsonResponse({'data': data})

@require_POST
# @login_required
def api_category_create(request):
    """Menambah kategori baru"""
    name = request.POST.get('name')
    icon = request.POST.get('icon')
    
    if name and icon:
        category = Category.objects.create(name=name, icon=icon)
        return JsonResponse({'status': 'success', 'message': 'Kategori berhasil dibuat'})
    
    return JsonResponse({'status': 'error', 'message': 'Data tidak lengkap'}, status=400)

@require_POST
# @login_required
def api_category_update(request, pk):
    """Memperbarui kategori yang sudah ada"""
    category = get_object_or_404(Category, pk=pk)
    name = request.POST.get('name')
    icon = request.POST.get('icon')
    
    if name and icon:
        category.name = name
        category.icon = icon
        category.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
# @login_required
def api_category_delete(request, pk):
    """Menghapus kategori"""
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return JsonResponse({'status': 'success'})

# --- HTML VIEW ---
def course_page(request):
    # Kita butuh daftar kategori untuk dropdown di Modal tambah/edit kursus
    categories = Category.objects.all()
    return render(request, 'courses/course_list.html', {'categories': categories})

# --- API VIEWS ---

def api_course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    data = []
    for c in courses:
        data.append({
            'id': c.id,
            'title': c.title,
            'category': c.category.name,
            'price': float(c.price),
            'level': c.get_level_display(),
            'is_published': c.is_published,
            'thumbnail': c.thumbnail.url if c.thumbnail else None,
        })
    return JsonResponse({'data': data})

@require_POST
def api_course_create(request):
    # Mengambil data teks dari POST dan file dari FILES
    title = request.POST.get('title')
    category_id = request.POST.get('category')
    thumbnail = request.FILES.get('thumbnail') # File Gambar
    short_description = request.POST.get('short_description')
    description = request.POST.get('description')
    price = request.POST.get('price', 0)
    level = request.POST.get('level', 'beginner')

    if title and category_id:
        category = get_object_or_404(Category, id=category_id)
        course = Course.objects.create(
            title=title,
            category=category,
            thumbnail=thumbnail,
            short_description=short_description,
            description=description,
            price=price,
            level=level,
            instructor=request.user if request.user.is_authenticated else None
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Data tidak lengkap'}, status=400)

@require_POST
def api_course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    # Update field teks
    course.title = request.POST.get('title', course.title)
    category_id = request.POST.get('category')
    if category_id:
        course.category = get_object_or_404(Category, id=category_id)
    
    course.short_description = request.POST.get('short_description', course.short_description)
    course.description = request.POST.get('description', course.description)
    course.price = request.POST.get('price', course.price)
    course.level = request.POST.get('level', course.level)
    course.is_published = request.POST.get('is_published') == 'true'

    # Update gambar jika ada file baru yang diunggah
    if request.FILES.get('thumbnail'):
        course.thumbnail = request.FILES.get('thumbnail')

    course.save()
    return JsonResponse({'status': 'success'})

@require_POST
def api_course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return JsonResponse({'status': 'success'})


# MODULE DAN CURRICULUM VIEW
def course_curriculum_page(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'courses/curriculum.html', {'course': course})

# --- MODULE API ---
def api_module_list(request, course_id):
    modules = Module.objects.filter(course_id=course_id).order_by('order')
    data = []
    for m in modules:
        lessons = m.lessons.all().values('id', 'title', 'duration_minutes', 'order')
        data.append({
            'id': m.id,
            'title': m.title,
            'order': m.order,
            'lessons': list(lessons)
        })
    return JsonResponse({'data': data})

@require_POST
def api_module_create(request, course_id):
    title = request.POST.get('title')
    order = request.POST.get('order', 0)
    if title:
        Module.objects.create(course_id=course_id, title=title, order=order)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# --- LESSON API ---
@require_POST
def api_lesson_create(request, module_id):
    title = request.POST.get('title')
    video_url = request.POST.get('video_url')
    content = request.POST.get('content')
    duration = request.POST.get('duration_minutes', 0)
    order = request.POST.get('order', 0)
    
    if title:
        Lesson.objects.create(
            module_id=module_id, 
            title=title, 
            video_url=video_url, 
            content=content, 
            duration_minutes=duration,
            order=order
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def api_module_delete(request, pk):
    get_object_or_404(Module, pk=pk).delete()
    return JsonResponse({'status': 'success'})

@require_POST
def api_lesson_delete(request, pk):
    get_object_or_404(Lesson, pk=pk).delete()
    return JsonResponse({'status': 'success'})

# QUIZ AND ASSESSMENT VIEWS CAN BE ADDED HERE

def quiz_detail_page(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    # Ambil atau buat quiz jika belum ada (karena OneToOne)
    quiz, created = Quiz.objects.get_or_create(
        module=module, 
        defaults={'title': f"Quiz {module.title}", 'passing_score': 70}
    )
    return render(request, 'courses/quiz.html', {'quiz': quiz, 'module': module})

def api_quiz_data(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = []
    for q in quiz.questions.all():
        answers = list(q.answers.all().values('id', 'text', 'is_correct'))
        questions.append({
            'id': q.id,
            'text': q.text,
            'answers': answers
        })
    return JsonResponse({'id': quiz.id, 'title': quiz.title, 'passing_score': quiz.passing_score, 'questions': questions})

@require_POST
def api_question_create(request, quiz_id):
    text = request.POST.get('text')
    if text:
        question = Question.objects.create(quiz_id=quiz_id, text=text)
        return JsonResponse({'status': 'success', 'id': question.id})
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def api_answer_add(request, question_id):
    text = request.POST.get('text')
    is_correct = request.POST.get('is_correct') == 'true'
    if text:
        Answer.objects.create(question_id=question_id, text=text, is_correct=is_correct)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def api_question_delete(request, pk):
    get_object_or_404(Question, pk=pk).delete()
    return JsonResponse({'status': 'success'})

# preview quiz take page
def quiz_take_page(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'courses/quiz_take.html', {'quiz': quiz})

# API untuk menilai jawaban kuis
def api_quiz_submit(request, quiz_id):
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, id=quiz_id)
        # Ambil data jawaban dari request (format: {question_id: answer_id})
        import json
        submitted_data = json.loads(request.body)
        user_answers = submitted_data.get('answers', {})

        total_questions = quiz.questions.count()
        correct_count = 0
        results = []

        for question in quiz.questions.all():
            answer_id = user_answers.get(str(question.id))
            is_correct = False
            correct_answer = question.answers.filter(is_correct=True).first()

            if answer_id:
                selected_answer = Answer.objects.filter(id=answer_id).first()
                if selected_answer and selected_answer.is_correct:
                    correct_count += 1
                    is_correct = True
            
            results.append({
                'question': question.text,
                'is_correct': is_correct,
                'correct_answer': correct_answer.text if correct_answer else "Belum diatur"
            })

        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        passed = score >= quiz.passing_score

        return JsonResponse({
            'score': round(score, 2),
            'passed': passed,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'results': results
        })
        
# PROJECT VIEWS
# --- VIEW HTML ---
def project_manager_page(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    # Ambil atau buat project jika belum ada
    project, created = Project.objects.get_or_create(
        module=module,
        defaults={'title': f"Project: {module.title}", 'instructions': 'Silakan isi instruksi pengerjaan di sini.'}
    )
    return render(request, 'courses/project_manager.html', {'project': project, 'module': module})

# --- API VIEWS ---
def api_project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return JsonResponse({
        'id': project.id,
        'title': project.title,
        'instructions': project.instructions,
        'template_url': project.template_file.url if project.template_file else None
    })

@require_POST
def api_project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.title = request.POST.get('title', project.title)
    project.instructions = request.POST.get('instructions', project.instructions)
    
    if request.FILES.get('template_file'):
        project.template_file = request.FILES.get('template_file')
        
    project.save()
    return JsonResponse({'status': 'success', 'message': 'Project berhasil diperbarui'})
