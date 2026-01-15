from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# --- MODELO DE IDENTIDADE GLOBAL ---
class Profile(models.Model):
    """
    Representa a identidade social global do usuário, independente da instituição.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_profile')
    global_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    
    # Lógica de Privacidade: Se True, seguidores precisam de aprovação (estilo FB/IG Privado)
    is_private = models.BooleanField(default=False)
    
    avatar = models.ImageField(upload_to='social/avatars/', blank=True, null=True)
    capa = models.ImageField(upload_to='social/covers/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    hobby = models.CharField(max_length=100, blank=True)
    visao_mundo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

# --- SISTEMA DE CONEXÕES HÍBRIDO ---
class Friendship(models.Model):
    """
    Gerencia Amizades (Turma) e Seguidores (Global).
    """
    STATUS_CHOICES = [
        ('PENDING', 'Solicitação Pendente'),
        ('ACCEPTED', 'Amigos (Mútua/Turma)'),
        ('FOLLOWING', 'Seguindo (Unilateral)'),
        ('BLOCKED', 'Bloqueado')
    ]

    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follower_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return f"{self.user_from} -> {self.user_to} ({self.status})"

# --- CONTEÚDO E INTERAÇÃO ---
class Post(models.Model):
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    conteudo = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='posts/img/', blank=True, null=True)
    video = models.FileField(upload_to='posts/video/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    curtidas = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='posts_curtidos', blank=True)
    
    VISIBILIDADE_CHOICES = [
        ('PUBLIC', 'Público'),
        ('FRIENDS', 'Amigos'),
        ('PRIVATE', 'Privado')
    ]
    visibilidade = models.CharField(max_length=10, choices=VISIBILIDADE_CHOICES, default='PUBLIC')

    def __str__(self):
        return f"Post de {self.autor} em {self.data_criacao}"

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

class Grupo(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField(blank=True)
    capa = models.ImageField(upload_to='grupos/', blank=True, null=True)
    membros = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='grupos_participa', blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='grupos_admin', blank=True)
    criador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grupos_criados', null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateTimeField()
    local = models.CharField(max_length=200)
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='eventos_confirmados', blank=True)

class Conversa(models.Model):
    participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversas')
    atualizado_em = models.DateTimeField(auto_now=True)
    is_ai_chat = models.BooleanField(default=False)

class Mensagem(models.Model):
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='caused_notifications', on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    target_post = models.ForeignKey('Post', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} {self.verb}"

class Story(models.Model):
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    imagem = models.ImageField(upload_to='stories/img/', blank=True, null=True)
    video = models.FileField(upload_to='stories/video/', blank=True, null=True)
    legenda = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.expira_em:
            self.expira_em = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

class Denuncia(models.Model):
    TIPOS = [
        ('BULLYING', 'Bullying ou Assédio'),
        ('SPAM', 'Spam ou Golpe'),
        ('VIOLENCIA', 'Violência ou Ameaça'),
        ('OUTRO', 'Outro Motivo'),
    ]
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='denuncias_feitas')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    resolvido = models.BooleanField(default=False)