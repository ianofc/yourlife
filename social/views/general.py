from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator
from ..models import Notification, Post
import random

@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user)
    notifs.update(is_read=True)
    return render(request, 'social/notifications/list.html', {'notifications': notifs})

@login_required
def global_premium(request):
    return render(request, 'social/premium/index.html')

@login_required
def settings_support(request):
    return render(request, 'social/settings/support.html')

@login_required
def settings_theme(request):
    return render(request, 'social/settings/theme.html')

@login_required
def explore(request):
    page_number = request.GET.get('page', 1)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    hero_post = None
    grid_items = []
    
    # === 1. HERO POST (Apenas na carga inicial) ===
    if str(page_number) == '1' and not is_ajax:
        # Tenta buscar do banco
        hero_obj = Post.objects.filter(video__isnull=False).exclude(video='').order_by('?').first()
        if not hero_obj:
            hero_obj = Post.objects.filter(imagem__isnull=False).exclude(imagem='').order_by('?').first()
            
        if hero_obj:
            try:
                hero_post = {
                    'titulo': hero_obj.autor.get_full_name(),
                    'descricao': hero_obj.legenda,
                    'video_url': hero_obj.video.url if hero_obj.video else None,
                    'imagem_url': hero_obj.imagem.url if hero_obj.imagem else None,
                    'is_video': bool(hero_obj.video),
                    'likes_count': hero_obj.curtidas.count(),
                    'comments_count': hero_obj.comentarios.count()
                }
            except:
                hero_post = None # Arquivo corrompido ou ausente

        # Fallback se não achar nada (Placeholder)
        if not hero_post:
            hero_post = {
                'titulo': 'Bem vindo ao NioChromaFeed',
                'descricao': 'Descubra as tendências visuais mais impactantes da nossa comunidade global.',
                'imagem_url': 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=1600&q=80',
                'video_url': None,
                'is_video': False,
                'likes_count': '15.2K',
                'comments_count': '342'
            }

    # === 2. GRID ITEMS (Com Paginação) ===
    queryset = Post.objects.filter(
        models.Q(imagem__isnull=False) & ~models.Q(imagem='') | 
        models.Q(video__isnull=False) & ~models.Q(video='')
    ).order_by('-data_criacao')

    # Paginação: 12 itens por vez
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(page_number)
    
    for post in page_obj:
        try:
            m_url = None
            is_vid = False
            
            if post.video:
                m_url = post.video.url
                is_vid = True
            elif post.imagem:
                m_url = post.imagem.url
            
            if m_url:
                grid_items.append({
                    'media_url': m_url,
                    'is_video': is_vid,
                    'is_tall': is_vid, # Regra: Vídeo = Vertical
                    'likes_count': post.curtidas.count(),
                    'comments_count': post.comentarios.count(),
                    'obj': post,
                    'caption': post.legenda,
                    'user_name': post.autor.get_full_name(),
                    'user_avatar': post.autor.profile.avatar.url if hasattr(post.autor, 'profile') and post.autor.profile.avatar else None
                })
        except:
            continue

    # === 3. FALLBACK GRID (Se banco vazio) ===
    # Se estamos na página 1 e não achou nada no banco, enche de placeholders
    if str(page_number) == '1' and not grid_items:
        placeholders = [
            {'img': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800', 'vid': False},
            {'img': 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=800', 'vid': True},
            {'img': 'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=800', 'vid': False},
            {'img': 'https://images.unsplash.com/photo-1552083375-1447ce886485?w=800', 'vid': False},
            {'img': 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800', 'vid': True},
            {'img': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800', 'vid': False},
            {'img': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800', 'vid': False},
            {'img': 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800', 'vid': False},
            {'img': 'https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=800', 'vid': True},
        ]
        for p in placeholders:
            grid_items.append({
                'media_url': p['img'],
                'is_video': p['vid'],
                'is_tall': p['vid'],
                'likes_count': f"{random.randint(100, 999)}K",
                'comments_count': f"{random.randint(20, 100)}",
                'caption': 'Conteúdo sugerido para você.',
                'user_name': 'Sugestão Nio',
                'user_avatar': None
            })

    context = {
        'hero_post': hero_post,
        'grid_items': grid_items,
        'has_next': page_obj.has_next() if 'page_obj' in locals() and page_obj.object_list else False
    }

    # Se for AJAX, retorna só o HTML dos itens novos
    if is_ajax:
        return render(request, 'social/search/partials/grid_items.html', context)

    # Carga normal
    return render(request, 'social/search/explore.html', context)
