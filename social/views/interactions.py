from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from ..models import Post, Comentario, Notification

# --- LIKES ---
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.curtidas.all():
        post.curtidas.remove(request.user) # Remove (Descurtir)
    else:
        post.curtidas.add(request.user) # Adiciona (Curtir)
        if post.autor != request.user:
            Notification.objects.create(recipient=post.autor, actor=request.user, verb="curtiu sua publicação", target_post=post)
    return redirect(request.META.get('HTTP_REFERER', 'yourlife_social:home'))

# --- COMENTÁRIOS ---
@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    texto = request.POST.get('comentario')
    if texto:
        Comentario.objects.create(post=post, autor=request.user, texto=texto)
        if post.autor != request.user:
            Notification.objects.create(recipient=post.autor, actor=request.user, verb="comentou na sua publicação", target_post=post)
    return redirect(request.META.get('HTTP_REFERER', 'yourlife_social:home'))

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comentario, id=comment_id)
    # Dono do comentário OU Dono do post pode apagar
    if request.user == comment.autor or request.user == comment.post.autor:
        comment.delete()
        messages.success(request, "Comentário removido.")
    return redirect(request.META.get('HTTP_REFERER', 'yourlife_social:home'))

# --- POSTS ---
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.autor:
        post.delete()
        messages.success(request, "Publicação excluída.")
    return redirect(request.META.get('HTTP_REFERER', 'yourlife_social:home'))

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.autor:
        return redirect('yourlife_social:home')
    
    if request.method == 'POST':
        post.conteudo = request.POST.get('texto')
        post.save()
        messages.success(request, "Publicação atualizada.")
        return redirect('yourlife_social:home')
    
    return render(request, 'social/feed/edit_post.html', {'post': post})

@login_required
def share_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)
    Post.objects.create(
        autor=request.user, 
        conteudo=f"Compartilhou de {original.autor.get_full_name()}:\n{original.conteudo}",
        imagem=original.imagem
    )
    if original.autor != request.user:
        Notification.objects.create(recipient=original.autor, actor=request.user, verb="compartilhou sua publicação", target_post=original)
    return redirect('yourlife_social:home')
