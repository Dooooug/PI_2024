from django.urls import path
from . import views
from .views import home, area_do_professor, quem_somos, cadastrar,valida_aluno_cadastro,cadastro_aluno,ver_alunos,excluir_aluno,editar_aluno,valida_edicao_cadastro

urlpatterns = [
    path("cadastro-de-alunos/", views.cadastrar, name="cadastro_alunos"),
    path("", views.home, name="home"),
    path("area-do-professor/", views.area_do_professor, name="area_do_professor"),
    path("quem-somos/", views.quem_somos, name="quem_somos"),
    path("valida-aluno-cadastro/",views.valida_aluno_cadastro,name="validando_cadastro"),
    path("valida-edicao-cadastro/",views.valida_edicao_cadastro,name="validando_edicao_cadastro"),
    path("quemsou/", views.cadastro_aluno, name="cadastro_aluno"),
    path("ver-alunos/", views.ver_alunos, name="ver_alunos"),
    path("ver-alunos/editar-alunos/<int:pk>/", views.editar_aluno, name='editar_aluno'),
    path("ver-alunos/excluir-alunos/<int:pk>/", views.excluir_aluno, name='excluir_aluno')
]
