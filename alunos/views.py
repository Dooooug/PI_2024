from sqlite3 import IntegrityError
from urllib import request
from django.shortcuts import redirect, render
from django.http import HttpResponse
from usuarios.models import Usuario
from .models import Alunos
from datetime import datetime
from django.utils import timezone
import re



def home(request):
    return render(request, 'home.html')

def area_do_professor(request):
    return render(request, 'login.html')

def quem_somos(request):
    return render (request,'quemsomos.html')
    
def cadastrar(request):
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        return render(request, 'cadastro_alunos.html', {'usuario_logado': request.session.get('usuario')})
    else:
        return redirect('/auth/login/?status=2')

def valida_aluno_cadastro(request):
    status = request.GET.get("status")
    return render(request, "cadastro_alunos.html", {"status": status})

def cadastro_aluno(request):
    if request.method == 'POST':
         data_inicio = request.POST.get("data_inicio")
    if not data_inicio:
            data_inicio = timezone.now().date()
    else:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()

    nome = request.POST.get("nome")
    sobrenome = request.POST.get("sobrenome")
    endereco = request.POST.get("endereco")
    idade = request.POST.get("idade")
    if not idade:
         idade=0

    cpf = request.POST.get("cpf")
    regex_cpf = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    if not regex_cpf.match(cpf):
        return redirect("/valida-aluno-cadastro/?status=2")
    
    celular = request.POST.get("celular")
    regex_celular = re.compile(r'^\(\d{2}\) \d{5}-\d{4}$')
    if not regex_celular.match(celular):
        return redirect("/valida-aluno-cadastro/?status=2")
    
    anamnesis = request.POST.get("anamnesis")
    gympass = request.POST.get("gympass")
    if gympass =="true":
        gympass = True
    elif gympass =="false":
        gympass = False
    else:
        gympass = None
    
    plano_escolhido = request.POST.get("plano_escolhido")
    data_pagamento = request.POST.get ("data_pagamento")
    if not data_pagamento:
            data_pagamento = timezone.now().date()
    else:
            data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date()

    if len(nome.strip()) == 0 or len(celular.strip()) == 0:
        return redirect("/valida-aluno-cadastro/?status=1")

    if Alunos.objects.filter(cpf=cpf).exists():
        return redirect("/valida-aluno-cadastro/?status=3")
        
        
    try:
            aluno = Alunos.objects.create(
                data_inicio=data_inicio,
                nome=nome,
                sobrenome=sobrenome,
                endereco=endereco,
                idade=idade,
                cpf=cpf,
                celular=celular,
                anamnesis=anamnesis,
                gympass=gympass,
                plano_escolhido=plano_escolhido,
                data_pagamento=data_pagamento
            )
            aluno.save()

            return redirect("/valida-aluno-cadastro/?status=0")
    except:
            return redirect("/valida-aluno-cadastro/?status=4")
                
def ver_alunos(request):
    Aluno = Alunos.objects.all()
    if request.method == 'POST':
        Alunos.objects.all().delete()
    return render(request, 'ver_alunos.html', {'Aluno': Aluno})