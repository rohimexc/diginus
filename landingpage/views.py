# program/views.py
from django.shortcuts import render
from program.models import Program
from courses.models import Course
from services.models import Service
from .models import ProjectDone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

def index(request):
    programs = Program.objects.all().order_by('-id')  # Ambil semua program
    courses = Course.objects.filter(is_published=True).order_by('-id')
    services = Service.objects.filter(is_published=True).order_by('-id')
    completed_projects = ProjectDone.objects.filter(is_active=True).order_by('-id')
    
    context = {
        'programs': programs,
        'courses': courses,
        'services': services,
        'completed_projects': completed_projects,
    }
    return render(request, 'landingpage/index.html', context)

@login_required
def project_list(request):
    return render(request, 'landingpage/project_list.html')

@login_required
def project_add(request):
    """Endpoint untuk menambahkan projek baru via AJAX"""
    if request.method == 'POST':
        title = request.POST.get('title')
        logo = request.FILES.get('logo')
        
        if not title or not logo:
            return JsonResponse({'status': 'error', 'message': 'Judul dan Logo wajib diisi'}, status=400)

        ProjectDone.objects.create(
            title=title,
            description=request.POST.get('description', ''),
            url=request.POST.get('url', ''),
            order=request.POST.get('order', 0),
            logo=logo
        )
        return JsonResponse({'status': 'success', 'message': 'Projek berhasil ditambahkan!'})
    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan'}, status=405)

@login_required
def project_edit(request, pk):
    """Endpoint untuk memperbarui projek yang sudah ada via AJAX"""
    project = get_object_or_404(ProjectDone, pk=pk)
    if request.method == 'POST':
        project.title = request.POST.get('title', project.title)
        project.description = request.POST.get('description', project.description)
        project.url = request.POST.get('url', project.url)
        project.order = request.POST.get('order', project.order)
        
        if request.FILES.get('logo'):
            project.logo = request.FILES.get('logo')
            
        project.save()
        return JsonResponse({'status': 'success', 'message': 'Projek berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan'}, status=405)

@login_required
def project_delete(request, pk):
    """Endpoint untuk menghapus projek via AJAX"""
    if request.method == 'POST':
        project = get_object_or_404(ProjectDone, pk=pk)
        project.delete()
        return JsonResponse({'status': 'success', 'message': 'Projek berhasil dihapus'})
    return JsonResponse({'status': 'error', 'message': 'Permintaan tidak valid'}, status=400)

def get_projects(request):
    """API untuk mengambil data projek (digunakan oleh tabel admin dan landing page)"""
    projects = ProjectDone.objects.all().order_by('order', '-created_at')
    data = []
    for p in projects:
        data.append({
            'id': p.id,
            'title': p.title,
            'logo_url': p.logo.url if p.logo else None,
            'description': p.description or "",
            'url': p.url or "",
            'order': p.order
        })
    return JsonResponse({'projects': data})