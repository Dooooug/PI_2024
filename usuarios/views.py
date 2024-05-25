from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Usuario
from hashlib import sha256
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password


def login(request):
    if request.session.get("usuario"):
        return redirect("cadastro-de-alunos/")
    status = request.GET.get("status")
    return render(request, "login.html", {"status": status})


def cadastro(request):
    status = request.GET.get("status")
    return render(request, "cadastro.html", {"status": status})


def valida_cadastro(request):

    nome = request.POST.get("nome", "")
    senha = request.POST.get("senha", "")
    email = request.POST.get("email", "")

    if len(nome.strip()) == 0 or len(email.strip()) == 0:
        return redirect("/auth/cadastro/?status=1")

    if len(senha) < 8:
        return redirect("/auth/cadastro/?status=2")

    if Usuario.objects.filter(email=email).exists():
        return redirect("/auth/cadastro/?status=3")

    try:
        senha = sha256(senha.encode()).hexdigest()
        usuario = Usuario(nome=nome, senha=senha, email=email)
        usuario.save()

        return redirect("/auth/cadastro/?status=0")
    except:
        return redirect("/auth/cadastro/?status=4")


def validar_login(request):
    email = request.POST.get("email")
    senha = request.POST.get("senha")

    senha = sha256(senha.encode()).hexdigest()

    usuario = Usuario.objects.filter(email=email).filter(senha=senha)

    if len(usuario) == 0:
        return redirect("/auth/login/?status=1")
    elif len(usuario) > 0:
        request.session["usuario"] = usuario[0].id
        return redirect(f"cadastro_alunos")  

    return HttpResponse(f"{email} {senha}")


def sair(request):
    request.session.flush()
    return redirect("/auth/login/")
