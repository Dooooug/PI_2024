from django.db import models
from datetime import date
import datetime
from usuarios.models import Usuario




class Alunos(models.Model):
    data_inicio = models.DateField(default="Escolha a data de inicio")
    nome = models.CharField(max_length=30, default="Digite o nome")
    sobrenome = models.CharField(max_length=30, default="Digite o Sobrenome")
    endereco = models.CharField(max_length=100, default="Digite o endereço")
    idade = models.IntegerField(default=18)
    cpf = models.CharField(max_length=11, default="Digite seu CPF")
    celular = models.CharField(max_length=15, default="")
    anamnesis = models.TextField(max_length=500, default="Qual são as suas queixas?")
    gympass = models.BooleanField(default=False)
    plano_escolhido = models.CharField(
        max_length=20,
        choices=[
            ("1x", "1x na semana"),
            ("2x", "2x na semana"),
            ("3x", "3x na semana"),
        ],
        default="1x",
    )
    data_pagamento = models.DateField(default="Escolha um data de pagamento")

    class Meta:
        verbose_name = "Aluno"

    def __str__(self) -> str:
        return f"{self.nome} {self.sobrenome}"
    
    def __str__(self) -> str:
        return f"{self.gympass}"




  


