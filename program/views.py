import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Program
from io import BytesIO
from openpyxl import Workbook
from html import escape
import json

def index(request):
    return render(request, 'program/index.html')

class ProgramDataTablesView(View):
    def post(self, request, *args, **kwargs):
        draw = int(request.POST.get('draw', 1))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')

        programs = Program.objects.all()

        if search_value:
            programs = programs.filter(
                Q(nama__icontains=search_value) |
                Q(jenis__icontains=search_value) |
                Q(level__icontains=search_value)
            )

        total_records = programs.count()

        # Pagination
        paginator = Paginator(programs, length)
        page_number = start // length + 1
        page_obj = paginator.get_page(page_number)

        data = []
        for obj in page_obj:
            # Escape teks
            nama_attr = escape(str(obj.nama))
            deskripsi_attr = escape(str(obj.deskripsi or ''))
            
            # Format tanggal (aman untuk string)
            pendaftaran_mulai_str = obj.pendaftaran_mulai.isoformat() if obj.pendaftaran_mulai else ''
            pendaftaran_tutup_str = obj.pendaftaran_tutup.isoformat() if obj.pendaftaran_tutup else ''
            pelaksanaan_mulai_str = obj.pelaksanaan_mulai.isoformat() if obj.pelaksanaan_mulai else ''
            pelaksanaan_selesai_str = obj.pelaksanaan_selesai.isoformat() if obj.pelaksanaan_selesai else ''

            # Build actions string (gunakan f-string dengan variabel yang sudah dihitung)
            actions = (
                f'<button class="btn-edit bg-yellow-500 text-white px-2 py-1 rounded text-xs mr-1" '
                f'data-id="{obj.id}" '
                f'data-nama="{nama_attr}" '
                f'data-deskripsi="{deskripsi_attr}" '
                f'data-harga="{obj.harga}" '
                f'data-jenis="{obj.jenis}" '
                f'data-level="{obj.level or ""}" '
                f'data-pendaftaran_mulai="{pendaftaran_mulai_str}" '
                f'data-pendaftaran_tutup="{pendaftaran_tutup_str}" '
                f'data-pelaksanaan_mulai="{pelaksanaan_mulai_str}" '
                f'data-pelaksanaan_selesai="{pelaksanaan_selesai_str}" '
                f'>Edit</button>'
                f'<button class="btn-delete bg-red-500 text-white px-2 py-1 rounded text-xs" data-id="{obj.id}">Hapus</button>'
            )
        
            data.append({
                "nama": obj.nama,
                "jenis": obj.jenis,
                "harga": f"Rp {obj.harga:,.0f}",
                "level": obj.get_level_display() if obj.jenis == 'Courses' else '-',
                "actions": actions
            })
        return JsonResponse({
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": total_records,
            "data": data
        })

@csrf_exempt
def create_or_update_program(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    program_id = request.POST.get('id')
    if program_id:
        program = get_object_or_404(Program, id=program_id)
    else:
        program = Program()

    program.nama = request.POST.get('nama', '').strip()
    program.deskripsi = request.POST.get('deskripsi', '').strip()
    program.harga = request.POST.get('harga', 0)
    program.jenis = request.POST.get('jenis', 'Courses')
    if program.jenis == 'Courses':
        program.level = request.POST.get('level', '')
    else:
        program.level = None

    program.pendaftaran_mulai = request.POST.get('pendaftaran_mulai') or None
    program.pendaftaran_tutup = request.POST.get('pendaftaran_tutup') or None
    program.pelaksanaan_mulai = request.POST.get('pelaksanaan_mulai') or None
    program.pelaksanaan_selesai = request.POST.get('pelaksanaan_selesai') or None

    if 'thumbnail' in request.FILES:
        program.thumbnail = request.FILES['thumbnail']

    program.save()
    return JsonResponse({'message': 'Berhasil disimpan!'})

@csrf_exempt
def delete_program(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    program_id = request.POST.get('id')
    if program_id:
        Program.objects.filter(id=program_id).delete()
        return JsonResponse({'message': 'Dihapus!'})
    return JsonResponse({'error': 'ID tidak ditemukan'}, status=400)

@csrf_exempt
def import_program(request):
    if request.method != 'POST' or 'import_file' not in request.FILES:
        return JsonResponse({'error': 'File tidak ditemukan'}, status=400)

    file = request.FILES['import_file']
    ext = file.name.split('.')[-1].lower()

    try:
        if ext in ['xlsx', 'xls']:
            df = pd.read_excel(file, engine='openpyxl' if ext == 'xlsx' else 'xlrd')
        elif ext == 'csv':
            df = pd.read_csv(file)
        else:
            return JsonResponse({'error': 'Format tidak didukung'}, status=400)

        for _, row in df.iterrows():
            Program.objects.create(
                nama=row.get('nama', ''),
                deskripsi=row.get('deskripsi', ''),
                harga=row.get('harga', 0),
                jenis=row.get('jenis', 'Courses'),
                level=row.get('level') if row.get('jenis') == 'Courses' else None,
                pendaftaran_mulai=row.get('pendaftaran_mulai'),
                pendaftaran_tutup=row.get('pendaftaran_tutup'),
                pelaksanaan_mulai=row.get('pelaksanaan_mulai'),
                pelaksanaan_selesai=row.get('pelaksanaan_selesai'),
            )
        return JsonResponse({'message': 'Import berhasil!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def export_program(request):
    programs = Program.objects.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Program"

    headers = ['nama', 'deskripsi', 'harga', 'jenis', 'level', 'pendaftaran_mulai', 'pendaftaran_tutup', 'pelaksanaan_mulai', 'pelaksanaan_selesai']
    ws.append(headers)

    for p in programs:
        ws.append([
            p.nama,
            p.deskripsi,
            float(p.harga),
            p.jenis,
            p.level if p.jenis == 'Courses' else '',
            p.pendaftaran_mulai,
            p.pendaftaran_tutup,
            p.pelaksanaan_mulai,
            p.pelaksanaan_selesai,
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=program_export.xlsx'
    return response