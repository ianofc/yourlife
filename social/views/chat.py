
from django.shortcuts import render
from django.http import JsonResponse
from ..models import Conversa, Mensagem
from core.services.ai_client import AIClient # Integração com Gemini/GPT

def enviar_mensagem(request):
    if request.method == 'POST':
        texto = request.POST.get('mensagem')
        conversa_id = request.POST.get('conversa_id')
        
        # Salva a mensagem do usuário
        msg = Mensagem.objects.create(
            sender=request.user,
            texto=texto,
            conversa_id=conversa_id
        )

        # Resposta Automática do Conscios (Se a conversa for com a IA)
        conversa = Conversa.objects.get(id=conversa_id)
        if conversa.is_ai_chat:
            ai_response = AIClient().ask(texto) # Chama seu serviço de IA
            Mensagem.objects.create(
                sender=None, # Sistema/IA
                texto=ai_response,
                conversa=conversa
            )
            return JsonResponse({'status': 'sent', 'response': ai_response})
            
        return JsonResponse({'status': 'sent'})
