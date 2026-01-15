from django.utils import timezone

def get_profile_context(user, is_me):
    # Tenta obter o perfil específico (Aluno ou Professor)
    aluno = getattr(user, 'aluno', None)
    professor = getattr(user, 'professor', None)
    
    # Define onde buscar a capa e avatar
    # Se o modelo CustomUser tiver 'avatar', usamos ele. Se não, tentamos no perfil.
    user_avatar = getattr(user, 'avatar', None) or getattr(user, 'foto', None)
    
    # A capa geralmente fica no perfil específico se não estiver no User
    user_cover = getattr(user, 'capa', None)
    if not user_cover and aluno:
        user_cover = getattr(aluno, 'capa', None)
    if not user_cover and professor:
        user_cover = getattr(professor, 'capa', None)

    # Verifica o que temos
    has_avatar = bool(user_avatar)
    has_cover = bool(user_cover)
    has_bio = bool(getattr(user, 'bio', None))
    
    # Lógica de Perfil Bebê
    is_baby = not (has_avatar and has_cover and has_bio)
    
    missing_items = []
    if not has_avatar: missing_items.append({'id': 'avatar', 'text': 'Adicionar foto', 'icon': 'fa-camera'})
    if not has_cover: missing_items.append({'id': 'cover', 'text': 'Adicionar capa', 'icon': 'fa-image'})
    if not has_bio: missing_items.append({'id': 'bio', 'text': 'Adicionar bio', 'icon': 'fa-pen'})

    return {
        'is_baby': is_baby,
        'missing_items': missing_items,
        'stats': {'friends_count': 0, 'photos_count': 0}, # Fake por enquanto
        'completion_percent': int(((3 - len(missing_items)) / 3) * 100),
        'cover_url': user_cover.url if user_cover else None, # URL segura da capa
        'avatar_url': user_avatar.url if user_avatar else None # URL segura do avatar
    }