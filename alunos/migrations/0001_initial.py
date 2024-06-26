# Generated by Django 5.0.4 on 2024-05-23 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Alunos",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data_inicio", models.DateField(default="2022-01-01")),
                ("nome", models.CharField(default="Digite o nome", max_length=30)),
                (
                    "sobrenome",
                    models.CharField(default="Digite o Sobrenome", max_length=30),
                ),
                (
                    "endereco",
                    models.CharField(default="Digite o endereço", max_length=100),
                ),
                ("data_nascimento", models.DateField(default="1990-01-01")),
                ("idade", models.IntegerField(default=18)),
                ("cpf", models.CharField(default="Digite seu CPF", max_length=11)),
                ("celular", models.CharField(default="", max_length=15)),
                (
                    "anamnesis",
                    models.TextField(
                        default="Qual são as suas queixas?", max_length=500
                    ),
                ),
                ("gympass", models.BooleanField(default=False)),
                (
                    "plano_escolhido",
                    models.CharField(
                        choices=[
                            ("1x", "1x na semana"),
                            ("2x", "2x na semana"),
                            ("3x", "3x na semana"),
                        ],
                        default="1x",
                        max_length=20,
                    ),
                ),
                (
                    "data_pagamento",
                    models.DateField(default="Escolha um data de pagamento"),
                ),
            ],
            options={
                "verbose_name": "Aluno",
            },
        ),
    ]
