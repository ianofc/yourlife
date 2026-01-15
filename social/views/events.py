from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class EventListView(LoginRequiredMixin, ListView):
    template_name = 'social/events/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Retorna lista vazia por enquanto para garantir que a pagina carregue
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
