import json
import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import CustomAuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..services.conscios_register import chat_com_conscios
from core.utils import gerar_matricula_conscios, gerar_email_institucional
from lumenios.pedagogico.models import Aluno

User = get_user_model()

# --- LOGIN & LOGOUT ---

def login_view(request):
    if request.user.is_authenticated:
        # CORREÇÃO: Redireciona para 'home' em vez de 'feed'
        return redirect('yourlife_social:home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # CORREÇÃO: Redireciona para 'home' em vez de 'feed'
            return redirect('yourlife_social:home')
        else:
            messages.error(request, "Matrícula ou senha inválidas.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'social/auth/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('yourlife_social:login')

# --- REGISTRO CONSCIOS ---

def register_view(request):
    if request.user.is_authenticated:
        # CORREÇÃO: Redireciona para 'home'
        return redirect('yourlife_social:home')
    return render(request, 'social/auth/register_conscios.html')

@require_POST
def api_conscios_chat(request):
    try:
        data = json.loads(request.body)
        historico = data.get('history', [])
        
        # Chama a IA
        resposta_ai = chat_com_conscios(historico)
        
        # --- FILTRO ANTI-CÓDIGO (REGEX) ---
        json_match = re.search(r'```json\s*({.*?})\s*```', resposta_ai, re.DOTALL | re.IGNORECASE)
        
        if not json_match:
            json_match = re.search(r'({.*"finalizado"\s*:\s*true.*})', resposta_ai, re.DOTALL | re.IGNORECASE)

        if json_match:
            try:
                json_str = json_match.group(1)
                dados_final = json.loads(json_str)
                
                if dados_final.get('finalizado'):
                    return JsonResponse({
                        'status': 'done', 
                        'data': dados_final 
                    })
            except json.JSONDecodeError:
                pass 
        
        resposta_limpa = re.sub(r'```json.*?```', '', resposta_ai, flags=re.DOTALL).strip()
        if not resposta_limpa: resposta_limpa = resposta_ai

        return JsonResponse({'status': 'continue', 'reply': resposta_limpa})

    except Exception as e:
        print(f"Erro Chat API: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def api_finalize_registration(request):
    try:
        data = json.loads(request.body)
        raw_data = data.get('dados', {})
        
        nome_completo = raw_data.get('nome_completo', 'Novo Usuário')
        partes_nome = nome_completo.split()
        first_name = raw_data.get('first_name', partes_nome[0] if partes_nome else "")
        last_name = raw_data.get('last_name', " ".join(partes_nome[1:]) if len(partes_nome) > 1 else "")
        senha = raw_data.get('senha', '123456')
        
        tipo_usuario = raw_data.get('tipo_usuario', 'ALUNO').upper()
        cargo = raw_data.get('cargo_informado', '').lower() if raw_data.get('cargo_informado') else ''
        
        role_db = 'ALUNO_FREE'
        
        if 'FUNCIONARIO' in tipo_usuario or 'FUNCIONÁRIO' in tipo_usuario:
            if any(x in cargo for x in ['diretor', 'gestor']): role_db = 'DIRECAO'
            elif any(x in cargo for x in ['coord', 'pedagog']): role_db = 'COORDENACAO'
            elif any(x in cargo for x in ['prof', 'docente']): role_db = 'PROFESSOR_FREE'
            else: role_db = 'SECRETARIA'
        elif 'PROFESSOR' in tipo_usuario:
             role_db = 'PROFESSOR_FREE'

        matricula = gerar_matricula_conscios()
        email = gerar_email_institucional(f"{first_name} {last_name}")
        
        count = 1
        email_base, domain = email.split('@')
        while User.objects.filter(email=email).exists():
            email = f"{email_base}{count}@{domain}"
            count += 1

        user = User.objects.create_user(
            username=matricula,
            email=email,
            password=senha,
            first_name=first_name,
            last_name=last_name,
            role=role_db
        )
        
        if role_db == 'ALUNO_FREE':
            Aluno.objects.create(usuario=user, nome=nome_completo, matricula=matricula)
        
        login(request, user)
        
        return JsonResponse({
            'status': 'success',
            'matricula': matricula,
            'redirect': '/social/feed/' 
        })
        
    except Exception as e:
        print(f"Erro Finalize: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
