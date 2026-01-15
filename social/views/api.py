from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import Notification

@login_required
def get_notifications(request):
    # Busca as últimas 20 notificações
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20]
    
    data = []
    unread_count = 0
    
    for n in notifs:
        if not n.is_read:
            unread_count += 1
            
        # Determina ícone e cor baseado no verbo
        icon = "fas fa-bell"
        color = "bg-gray-500"
        
        if 'curtiu' in n.verb:
            icon = "fas fa-heart"
            color = "bg-rose-500"
        elif 'comentou' in n.verb:
            icon = "fas fa-comment"
            color = "bg-blue-500"
        elif 'aniversário' in n.verb:
            icon = "fas fa-birthday-cake"
            color = "bg-yellow-500"
        elif 'sistema' in n.verb: # Ex: Nota lançada
            icon = "fas fa-cog"
            color = "bg-slate-700"

        data.append({
            'id': n.id,
            'actor_name': n.actor.get_full_name(),
            'actor_avatar': n.actor.avatar.url if n.actor.avatar else f"https://ui-avatars.com/api/?name={n.actor.first_name}",
            'verb': n.verb,
            'time_ago': n.created_at.strftime("%d/%m %H:%M"), # Simplificado para JSON
            'icon': icon,
            'color': color,
            'is_read': n.is_read,
            # Link inteligente: Se for post social vai pro post, se for sistema vai pra URL
            'url': f"/social/post/{n.target_post.id}/like/" if n.target_post else "#" 
        })

    return JsonResponse({'notifications': data, 'unread_count': unread_count})

@login_required
def mark_as_read(request):
    if request.method == "POST":
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)