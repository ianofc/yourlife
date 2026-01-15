from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Post, Comentario

@login_required
def home_feed(request):
    # --- BLOQUEIO DE BEBÊ ---
    # Bebês não têm feed, vão direto para o Diário
    if request.user.nivel_ensino == 'bebe' or request.user.fase_vida == 'BEBE':
        return redirect('core:daily_diary')
    # ------------------------

    if request.method == 'POST':
        texto = request.POST.get('texto')
        imagem = request.FILES.get('imagem')
        video = request.FILES.get('video')
        
        if texto or imagem or video:
            Post.objects.create(
                autor=request.user,
                conteudo=texto,
                imagem=imagem,
                video=video
            )
        return redirect('yourlife_social:home')

    posts = Post.objects.all().order_by('-data_criacao')
    return render(request, 'social/feed/home.html', {'posts': posts})

@login_required
def reels_view(request):
    # Bebês também não veem Reels
    if request.user.nivel_ensino == 'bebe':
        return redirect('core:daily_diary')
        
    return render(request, 'social/reels/index.html')


from django.utils import timezone

@login_required
def create_story(request):
    if request.method == 'POST':
        imagem = request.FILES.get('imagem')
        video = request.FILES.get('video')
        legenda = request.POST.get('legenda')
        
        if imagem or video:
            from ..models import Story  # Importação local para evitar ciclo
            Story.objects.create(
                autor=request.user,
                imagem=imagem,
                video=video,
                legenda=legenda
            )
            return redirect('yourlife_social:home')
            
    return render(request, 'social/create/create_story.html')

