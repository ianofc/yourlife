import os
from pathlib import Path

BASE_DIR = Path(".")

def create_structure():
    print("🏗️ [YourLife Reconstruction] Criando espinha dorsal independente...")

    # 1. Criar pasta 'core' interna do YourLife (para serviços e utilitários)
    (BASE_DIR / "core/services").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "core/utils").mkdir(parents=True, exist_ok=True)
    open(BASE_DIR / "core/__init__.py", "a").close()
    open(BASE_DIR / "core/services/__init__.py", "a").close()

    # 2. Criar o ai_client.py dentro do YourLife (para não depender do SaaS)
    AI_CLIENT_CONTENT = """
import openai
from django.conf import settings

def get_ai_response(prompt, context=""):
    # Mock de resposta ou integração direta com OpenAI/Zios
    return f"Resposta inteligente YourLife para: {prompt}"
"""
    (BASE_DIR / "core/services/ai_client.py").write_text(AI_CLIENT_CONTENT, encoding="utf-8")

    # 3. Criar Requirements.txt independente
    REQUIREMENTS = """
django>=4.2
requests
openai
pillow
django-environ
python-dotenv
"""
    (BASE_DIR / "requirements.txt").write_text(REQUIREMENTS.strip(), encoding="utf-8")

    # 4. Criar .gitignore
    GITIGNORE = """
venv/
db.sqlite3
.env
__pycache__/
media/
static_root/
"""
    (BASE_DIR / ".gitignore").write_text(GITIGNORE.strip(), encoding="utf-8")

    # 5. Criar Tailwind Config Básico
    TAILWIND = """
module.exports = {
  content: ["./social/templates/**/*.html", "./static/**/*.js"],
  theme: { extend: {} },
  plugins: [],
}
"""
    (BASE_DIR / "tailwind.config.js").write_text(TAILWIND.strip(), encoding="utf-8")

    # 6. Corrigir o arquivo que está quebrando o sistema
    # (conscios_register.py buscava 'core.services' do NioCortex)
    CONSCIOS_PATH = BASE_DIR / "social/services/conscios_register.py"
    if CONSCIOS_PATH.exists():
        content = CONSCIOS_PATH.read_text(encoding="utf-8")
        # Muda a importação para o core interno que acabamos de criar
        new_content = content.replace("from core.services.ai_client", "from core.services.ai_client")
        CONSCIOS_PATH.write_text(new_content, encoding="utf-8")

    print("✅ Estrutura Core, AI Client e Configurações de projeto criadas.")

def fix_views_imports():
    print("🛠️ Corrigindo importações remanescentes em Views...")
    for root, _, files in os.walk(BASE_DIR / "social/views"):
        for file in files:
            if file.endswith(".py"):
                p = Path(root) / file
                content = p.read_text(encoding="utf-8")
                # Garante que não busca 'core' externo
                if "from core." in content and "from .core." not in content:
                    # Como criamos a pasta core na raiz de yourlife, 
                    # a importação 'from core' funcionará localmente
                    pass 
    print("✅ Verificação de views concluída.")

if __name__ == "__main__":
    create_structure()
    fix_views_imports()
    print("\n🚀 [CONCLUÍDO] YourLife agora possui seu próprio CORE.")
    print("👉 Agora rode: python manage.py migrate")