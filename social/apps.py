import os
import shutil
from pathlib import Path

# Configuração de caminhos baseada na estrutura do projeto
BASE_DIR = Path(".")
SOCIAL_APP_PATH = BASE_DIR / "yourlife" / "social"
STATIC_DIR = BASE_DIR / "static"
SOCIAL_STATIC_DEST = STATIC_DIR / "social"

def create_global_auth():
    print("🔐 [1/4] Criando Autenticação e Registro Global...")
    auth_dir = SOCIAL_APP_PATH / "views"
    auth_dir.mkdir(parents=True, exist_ok=True)
    
    auth_file = auth_dir / "auth_global.py"
    content = """from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.forms import UserCreationForm as CustomUserCreationForm
from ..models import Profile

class GlobalRegisterView(View):
    \"\"\"Permite o cadastro de usuários externos sem vínculo escolar.\"\"\"
    template_name = 'social/auth/register_global.html'

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tenant_type = 'GLOBAL' # Define como usuário da rede global
            user.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('yourlife:home')
        return render(request, self.template_name, {'form': form})
"""
    auth_file.write_text(content, encoding="utf-8")

def setup_auto_provisioning():
    print("📡 [2/4] Configurando Signals para Provisionamento Automático...")
    signals_file = SOCIAL_APP_PATH / "signals.py"
    content = """from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def provision_social_identity(sender, instance, created, **kwargs):
    \"\"\"Garante que todo novo usuário do sistema ganhe um Perfil YourLife.\"\"\"
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={'display_name': instance.get_full_name() or instance.username}
        )
"""
    signals_file.write_text(content, encoding="utf-8")

def migrate_static_assets():
    print("🎨 [3/4] Isolando Assets Estáticos (CSS/JS)...")
    # Cria estrutura de pastas sociais isoladas
    (SOCIAL_STATIC_DEST / "css" / "v2").mkdir(parents=True, exist_ok=True)
    (SOCIAL_STATIC_DEST / "js" / "common").mkdir(parents=True, exist_ok=True)

    # Mapeamento de arquivos a serem isolados
    assets = [
        (STATIC_DIR / "core/css/themes.css", SOCIAL_STATIC_DEST / "css/v2/core-identity.css"),
        (STATIC_DIR / "core/js/talkio.js", SOCIAL_STATIC_DEST / "js/common/talkio-global.js"),
    ]

    for src, dst in assets:
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✅ Isolado: {src.name}")

def update_fastapi_bridge():
    print("🌉 [4/4] Preparando Ponte de API no FastAPI...")
    fastapi_main = BASE_DIR / "fastapi_service" / "main.py"
    if fastapi_main.exists():
        bridge_code = """
@app.get("/api/v1/social/identity/{user_id}")
async def get_social_identity(user_id: str):
    \"\"\"Endpoint de consumo para o NioCortex buscar dados da YourLife.\"\"\"
    return {"status": "Global Identity Service Active"}
"""
        with open(fastapi_main, "a", encoding="utf-8") as f:
            f.write(bridge_code)

if __name__ == "__main__":
    print("🚀 Iniciando Transição para YourLife Global...")
    create_global_auth()
    setup_auto_provisioning()
    migrate_static_assets()
    update_fastapi_bridge()
    print("\n🏁 Configuração concluída. YourLife está pronta para a escala global.")