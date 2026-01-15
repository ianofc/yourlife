from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from core.forms import CustomUserCreationForm
from ..models import Profile

class GlobalRegisterView(View):
    template_name = 'social/auth/register_global.html'

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tenant_type = 'GLOBAL'
            user.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('yourlife:home')
        return render(request, self.template_name, {'form': form})
