from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from yourlife.social.models import Post, Friendship

User = get_user_model()

@login_required
def profile_detail(request, username=None):
    # --- BLOQUEIO DE BEBÊ ---
    # Bebês não têm perfil social público nem privado
    if request.user.nivel_ensino == 'bebe' or request.user.fase_vida == 'BEBE':
        return redirect('core:daily_diary')
    # ------------------------

    if username:
        username = username.strip('@')

    if username and username != request.user.username:
        profile_user = get_object_or_404(User, username=username)
        is_own_profile = False
    else:
        profile_user = request.user
        is_own_profile = True

    posts = Post.objects.filter(autor=profile_user).order_by('-data_criacao')
    posts_count = posts.count()
    friends_count = Friendship.objects.filter(user_from=profile_user, status='ACCEPTED').count()

    context = {
        'user': request.user,
        'profile_user': profile_user,
        'posts': posts,
        'is_own_profile': is_own_profile,
        'posts_count': posts_count,
        'friends_count': friends_count,
        'is_university': getattr(profile_user, 'nivel_ensino', '') == 'superior',
        'is_baby': getattr(profile_user, 'fase_vida', '') == 'BEBE',
    }

    return render(request, 'social/profile/profile_detail.html', context)

@login_required
def my_profile(request):
    return profile_detail(request, username=None)

@login_required
def user_profile(request, username):
    return profile_detail(request, username=username)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        if 'capa' in request.FILES:
            user.capa = request.FILES['capa']
            
        user.save()
        return redirect('yourlife_social:meu_perfil')
        
    return render(request, 'social/profile/edit_profile_fb.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        if 'capa' in request.FILES:
            user.capa = request.FILES['capa']
            
        user.save()
        return redirect('yourlife_social:meu_perfil')
        
    return render(request, 'social/profile/edit_profile_fb.html', {'user': request.user})
