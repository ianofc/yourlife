
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

@csrf_exempt
def receive_sync(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data.get('display_name', ''),
                'email': f"{data['username']}@yourlife.social"
            }
        )
        return JsonResponse({'status': 'synced', 'created': created}, status=201)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
