from django.urls import path
from . import views
from .views import home, area_do_professor, quem_somos, cadastrar,valida_aluno_cadastro,cadastro_aluno,ver_alunos

urlpatterns = [
    path("cadastro-de-alunos/", views.cadastrar, name="cadastro_alunos"),
    path("", views.home, name="home"),
    path("area-do-professor/", views.area_do_professor, name="area_do_professor"),
    path("quem-somos/", views.quem_somos, name="quem_somos"),
    path("valida-aluno-cadastro/",views.valida_aluno_cadastro,name="validando_cadastro"),
    path("cadastro_aluno/", views.cadastro_aluno, name="cadastro_aluno"),
    path("ver-alunos/", views.ver_alunos, name="ver_alunos")
]
