from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt

@login_required
@xframe_options_exempt
def conscios_view(request):
    return render(request, 'social/components/conscios_widget.html')

@login_required
@xframe_options_exempt
def talkio_app(request):
    return render(request, 'social/talkio/index.html')

@login_required
def support_page(request):
    return render(request, 'social/pages/support.html')

@login_required
def settings_page(request):
    return render(request, 'social/pages/settings.html')

@login_required
def settings_support(request):
    return support_page(request)

@login_required
def settings_theme(request):
    return render(request, 'social/pages/themes.html')

@login_required
def settings_a11y(request):
    return render(request, 'social/pages/accessibility.html')


from django.contrib import messages
from ..models import Denuncia

@login_required
def report_abuse(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao')
        anonimo = request.POST.get('anonimo') == 'on'
        
        autor = None if anonimo else request.user
        
        Denuncia.objects.create(
            autor=autor,
            tipo=tipo,
            descricao=descricao
        )
        messages.success(request, 'Sua denúncia foi recebida e será analisada pela nossa equipe de segurança.')
        return redirect('yourlife_social:support_page')
    
    return redirect('yourlife_social:support_page')

