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
import pytz
import telebot
import phonenumbers
from django.contrib import messages


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

def calcular_proxima_data_pagamento_srt(data_pagamento):
    data_pagamento_dt = datetime.strptime(data_pagamento, "%Y-%m-%d")  # Convert string to datetime
    proxima_data_pagamento = data_pagamento_dt + timedelta(days=30)
    return proxima_data_pagamento.strftime("%Y-%m-%d")

###def calcular_idade_str(data_nascimento):
  ##  data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d')  # assume que a data está no formato YYYY-MM-DD
   ## hoje = datetime.today()
  ##  idade = hoje.year - data_nascimento.year
  ##  if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
   ##     idade -= 1
   ## return idade

def calcular_idade_date(data_nascimento):
    hoje = datetime.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade
   
def cadastro_aluno(request):         ### Para inserir no banco de dados
    data_inicio = timezone.now().date()
    if request.method == 'POST':
        data_inicio = request.POST.get("data_inicio")
    nome = request.POST.get("nome")
    sobrenome = request.POST.get("sobrenome")
    endereco = request.POST.get("endereco")
    data_nascimento_str = request.POST.get("data_nascimento")
    data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
    idade = calcular_idade_date(data_nascimento)
    cpf = request.POST.get("cpf")
    regex_cpf = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    if not regex_cpf.match(cpf):
        return redirect("/valida-aluno-cadastro/?status=2")
    
    celular = request.POST.get("celular")
    if not celular.startswith("+55"):
         celular = "+55" + celular
    formatando_celular = phonenumbers.parse(celular, "BR")
    if not phonenumbers.is_valid_number(formatando_celular):
        return redirect("/valida-aluno-cadastro/?status=5")
    
    celular_formatado = phonenumbers.format_number(formatando_celular, phonenumbers.PhoneNumberFormat.NATIONAL)
    celular = celular_formatado

    anamnesis = request.POST.getlist("anamnesis[]")
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
        return redirect("/valida-aluno-cadastro/?status=1") # Redirecione para uma página de erro 

    if Alunos.objects.filter(cpf=cpf).exists():
        return redirect("/valida-aluno-cadastro/?status=3") # Redirecione para uma página de erro 
    
    if data_nascimento <= datetime(1900, 1, 1).date():
        return redirect("/valida-aluno-cadastro/?status=6")  # Redirecione para uma página de erro 
    
    try:
            aluno = Alunos.objects.create(
                data_inicio=data_inicio,
                nome=nome,
                sobrenome=sobrenome,
                endereco=endereco,
                data_nascimento=data_nascimento,
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
            aluno.idade = idade
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

def calcular_data_lembrete(data_pagamento, enviar_um_dia_antes=True):
    if enviar_um_dia_antes:
        data_lembrete = data_pagamento - timedelta(days=1)
    else:
        data_lembrete = data_pagamento + timedelta(days=1)
    return data_lembrete


TOKEN = "6943580812:AAGLmCbg6N2kzkdJ9uIn9xcqqBR165gU5lQ"
bot = telebot.TeleBot(TOKEN)

@shared_task
def enviar_mensagem(aluno):
    data_pagamento = aluno.data_pagamento
    data_lembrete = data_pagamento - timedelta(hours=12)

    mensagem =  f"Olá, {aluno.nome}! Lembre-se de efetuar o pagamento até {data_pagamento.strftime('%d/%m/%Y')}."

    try:
        chat_id = aluno.celular  # Substitua pelo número correto do aluno
        bot.send_message(chat_id, mensagem)
        print(f"Lembrete enviado para {aluno.nome} ({aluno.celular})")
    except Exception as e:
        print(f"Erro ao enviar lembrete para {aluno.nome}: {str(e)}")

def gerar_relatorio(alunos):
    relatorio = ""
    for aluno in alunos:
        relatorio += f"{aluno.nome}: {aluno.data_pagamento.strftime('%d/%m/%Y')}\n"
    return relatorio

# Exemplo de uso
if __name__ == "__main__":
    # Suponha que 'alunos' seja uma lista de objetos Aluno com atributos 'nome', 'data_pagamento' e 'numero_whatsapp'
    # Você deve adaptar isso conforme sua estrutura de dados
    alunos = ["{aluno.nome}"]# Preencha com seus alunos

    # Verifique os pagamentos e envie lembretes
    for aluno in alunos:
        enviar_mensagem(aluno)

    # Gere o relatório
    relatorio = gerar_relatorio(aluno)
    print("Relatório de Pagamentos:")
    print(relatorio)


    
def formatar_anamneses(anamneses):
    return "".join(anamneses).replace("'", "").replace("[", "").replace("]", "")


    
def ver_alunos(request):
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        Aluno = Alunos.objects.all()
        for aluno in Aluno:
            aluno.anamnesis = formatar_anamneses(aluno.anamnesis)
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
            data_inicio = request.POST.get('data_inicio', aluno.data_inicio)
            if not data_inicio or data_inicio == '':
                return redirect("/valida-edicao-cadastro/?status=1")
            aluno.data_inicio = data_inicio
            aluno.nome = request.POST.get('nome', aluno.nome)
            aluno.sobrenome = request.POST.get('sobrenome', aluno.sobrenome)
            aluno.endereco = request.POST.get('endereco', aluno.endereco)
            aluno.celular = request.POST.get('celular', aluno.celular)
            aluno.gympass = request.POST.get('gympass') == 'True'
            aluno.plano_escolhido = request.POST.get('plano_escolhido', aluno.plano_escolhido)

            anamnesis = request.POST.getlist("anamnesis[]", [])
            if anamnesis:
                aluno.anamnesis = formatar_anamneses(aluno.anamnesis)

            proxima_data_pagamento = calcular_proxima_data_pagamento_srt(aluno.data_inicio)
            aluno.data_pagamento = proxima_data_pagamento

            aluno.save()

            mensagem_confirmacao = f"Os dados do aluno {aluno.nome}{aluno.sobrenome} foram atualizados com sucesso!"
            return render(request, 'editar_alunos.html', {'Aluno': aluno, 'mensagem_confirmacao': mensagem_confirmacao})
        else:
            return render(request, 'editar_alunos.html', {'Aluno': aluno})
    else:
        return redirect('/auth/login/?status=2')
        
   
        
       
def valida_edicao_cadastro(request):
    status = request.GET.get("status")
    return render(request, 'ver_alunos.html', {"status": status})