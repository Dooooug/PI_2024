from urllib import request
from django.shortcuts import redirect, render,get_object_or_404
from django.http import HttpResponse
from usuarios.models import Usuario
from .models import Alunos
from datetime import datetime,timedelta
from django.utils import timezone
import re
import requests
from celery import shared_task
from django.core.mail import send_mail


def home(request): ### para renderizar o template home
    return render(request, 'home.html')

def area_do_professor(request): ### para renderizar o area do professor
    return render(request, 'login.html')

def quem_somos(request): ### para renderizar o template quem somos
    return render (request,'quemsomos.html')
    
def cadastrar(request):  ### Para confirmar se está logoda e exibir mensagem
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        return render(request, 'cadastro_alunos.html', {'usuario_logado': request.session.get('usuario')})
    else:
        return redirect('/auth/login/?status=2')

def valida_aluno_cadastro(request): ### Para exibir o status estabelecido no template
    status = request.GET.get("status")
    return render(request, "cadastro_alunos.html", {"status": status})

def calcular_proxima_data_pagamento(data_pagamento):
     proxima_data_pagamento = data_pagamento + timedelta(days=30)
     return proxima_data_pagamento

def cadastro_aluno(request):         ### Para inserir no banco de dados
    data_inicio = timezone.now().date()
    if request.method == 'POST':
         data_inicio = request.POST.get("data_inicio")
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
        return redirect("/valida-aluno-cadastro/?status=5")
    
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
                data_pagamento=data_pagamento,
                )
            

            proxima_data_pagamento= calcular_proxima_data_pagamento(data_pagamento)
            aluno.data_pagamento = proxima_data_pagamento
            aluno.save()

            return redirect("/valida-aluno-cadastro/?status=0")
    except:
            return redirect("/valida-aluno-cadastro/?status=4")


@shared_task
def verificar_pagamentos():    #### falta testar
    hoje = datetime.now().date()
    aluno = Alunos.objects.filter(data_pagamento__lte=hoje)
    for aluno in aluno:
        enviar_mensagem(aluno)
        aluno.data_pagamento = calcular_proxima_data_pagamento(aluno.data_pagamento)
        aluno.save()

def calcular_data_lembrete(data_pagamento):
    data_lembrete = data_pagamento - timedelta(hours=12)
    return data_lembrete





def enviar_mensagem(aluno):
    pass


    
def ver_alunos(request):
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        Aluno = Alunos.objects.all()  
        return render(request, 'ver_alunos.html', {'usuario_logado': request.session.get('usuario'), 'Aluno': Aluno})
    else:
        return redirect('/auth/login/?status=2')

def excluir_aluno(request, pk):
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        aluno = get_object_or_404(Alunos, pk=pk)
        if request.method == "POST":
            aluno.delete()
            return redirect('ver_alunos')
        else:
            return render(request, 'excluir_aluno.html', {'Aluno': aluno})
    else:
        return redirect('/auth/login/?status=2')
    
    
def editar_aluno(request, pk):
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        aluno = get_object_or_404(Alunos, pk=pk)

        if request.method == "POST":
            current_sobrenome = aluno.sobrenome
            current_nome = aluno.nome
            current_endereco = aluno.endereco
            current_idade = aluno.idade
            current_cpf = aluno.cpf

            data_inicio = request.POST.get('data_inicio')
            if not data_inicio or data_inicio == '':
                return redirect("/valida-edicao-cadastro/?status=1")
            aluno.data_inicio = data_inicio

            nome = request.POST.get('nome')
            if nome and nome != '':
                current_nome = nome
            aluno.nome = current_nome

            sobrenome = request.POST.get('sobrenome')
            if sobrenome and sobrenome != '':
                current_sobrenome = sobrenome
            aluno.sobrenome = current_sobrenome

            endereco = request.POST.get('endereco')
            if endereco and endereco != '':
                current_endereco = endereco
            aluno.endereco = current_endereco

            idade = request.POST.get('idade')
            if idade and idade != current_idade:
                current_idade = idade
            aluno.idade = current_idade

            cpf = request.POST.get('cpf')
            if cpf and cpf != '':
                current_cpf = cpf
            aluno.cpf = current_cpf

            aluno.celular = request.POST.get('celular')

            anamesis = request.POST.get('anamnesis')
            if not anamesis or anamesis == '':
                return redirect("/valida-edicao-cadastro/?status=1")

            aluno.anamnesis = anamesis

            aluno.gympass = request.POST.get('gympass') == 'True'
            aluno.plano_escolhido = request.POST.get('plano_escolhido')

            aluno.save()
        

           
        return render(request, 'editar_alunos.html', {'Aluno': aluno})
    else:
        return redirect('/auth/login/?status=2')
        
def valida_edicao_cadastro(request):
    status = request.GET.get("status")
    return render(request, "controle.html", {"status": status})