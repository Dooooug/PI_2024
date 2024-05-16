import os
from celery import Celery

# Defina a variável de ambiente para o módulo de configurações do Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro')

app = Celery('alunos')

# Use as configurações do Django para configurar o Celery.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregue automaticamente as tarefas de todos os aplicativos Django registrados.
app.autodiscover_tasks()
