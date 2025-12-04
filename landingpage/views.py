# program/views.py
from django.shortcuts import render
from program.models import Program

def index(request):
    programs = Program.objects.all().order_by('-id')  # Ambil semua program
    return render(request, 'landingpage/index.html', {'programs': programs})