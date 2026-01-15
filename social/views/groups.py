from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
# Tenta importar o modelo, se não existir, usa lista vazia para não quebrar
try:
    from yourlife.social.models import Grupo
except ImportError:
    Grupo = None

class GroupListView(LoginRequiredMixin, ListView):
    template_name = 'social/groups/list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        if Grupo:
            return Grupo.objects.all()
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
