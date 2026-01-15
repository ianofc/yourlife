from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Friendship

@login_required
def friends_list(request):
    # Lista de amigos confirmados
    amigos = Friendship.objects.filter(
        from_user=request.user, 
        status='aceito'
    )
    return render(request, 'social/friends/list.html', {'amigos': amigos})

@login_required
def friend_requests(request):
    # Solicitações pendentes recebidas
    solicitacoes = Friendship.objects.filter(
        to_user=request.user, 
        status='pendente'
    )
    return render(request, 'social/friends/requests.html', {'requests': solicitacoes})