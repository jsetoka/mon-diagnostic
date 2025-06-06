

# diagnostic/views.py
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from .utils.jwt_utils import decode_token, generate_access_token, generate_refresh_token
import json
import jwt
from datetime import datetime, timedelta
from .models import Vehicule
from django.contrib.auth import get_user_model

# def accueil(request):
#     return HttpResponse("Bienvenue sur la plateforme de diagnostic")

from django.shortcuts import get_object_or_404, redirect, render
import jwt

from diagnostic.forms import VehiculeForm
from diagnostic.models import Vehicule

def tableau_de_bord(request):
    return render(request, 'diagnostic/dashbord.html', {
        'nom': 'LAFEE',
        'prenom': 'Tabitha',
        'diagnostics': ['Moteur', 'Frein', 'Électronique']
    })

def vehicule_list(request):
    vehicules = Vehicule.objects.filter()
    return render(request, 'diagnostic/vehicule_list.html', {
      'vehicules': vehicules,
    })  
    
def ajouter_vehicule(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.proprietaire = request.user
            vehicule.save()
            return redirect('vehicule_list')
    else:
        form = VehiculeForm()
    return render(request, 'diagnostic/ajouter_vehicule.html', {'form': form})


def vehicule_update(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    form = VehiculeForm(request.POST or None, instance=vehicule)
    if form.is_valid():
        form.save()
        return redirect('vehicule_list')
    return render(request, 'diagnostic/modifier_vehicule.html', {'form': form})

def vehicule_delete(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        return redirect('vehicule_list')
    return render(request, 'diagnostic/confirm_delete.html', {'vehicule': vehicule})


def get_user_from_request(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        print("❌ Aucun header Authorization")
        return None
    
    if not auth_header.startswith("Bearer "):
        print("❌ Format incorrect. Attendu : Bearer <token>")
        return None

    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        print("❌ Token invalide ou expiré")
        return None

    user_id = payload.get("user_id")
    if not user_id:
        print("❌ Aucun user_id dans le token")
        return None

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        print("❌ Utilisateur introuvable")
        return None


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

@csrf_exempt
def api_login(request):
    print('jojo')
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data)
            username = data['username']
            password = data['password']
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Requête invalide. JSON attendu avec username et password.'}, status=400)

        user = authenticate(username=username, password=password)
        if user:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            return JsonResponse({
                'access': access_token,
                'refresh': refresh_token
            })
        else:
            return JsonResponse({'error': 'Identifiants invalides.'}, status=401)
    
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def api_refresh_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            refresh_token = data['refresh']
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            if payload.get('type') != 'refresh':
                return JsonResponse({'error': 'Type de token invalide'}, status=401)

            # Recréer un access token
            user_id = payload['user_id']
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)

            new_access_token = generate_access_token(user)
            return JsonResponse({'access': new_access_token})

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Refresh token expiré'}, status=401)
        except (jwt.InvalidTokenError, KeyError, User.DoesNotExist):
            return JsonResponse({'error': 'Token invalide'}, status=401)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
  



def api_vehicule_list(request):
    auth_header = request.headers.get("Authorization")  # ✅ récupère le header
    print(request.headers)
    if not auth_header:
        return None
    
    if not auth_header.startswith("Bearer "):
        print("❌ Format incorrect. Attendu : Bearer <token>")
        return None
    
    token = auth_header.split(" ")[1]  # ✅ extrait le token après "Bearer"
    
    payload = decode_token(token)
    if not payload:
        return JsonResponse({'error': 'Token invalide ou manquant'}, status=401)

    vehicules = Vehicule.objects.all()
    # Crée une liste de dictionnaires à partir des objets
    data = [
        {
            "id": v.id,
            "marque": v.marque,
            "modele": v.modele,
            "immatriculation": v.immatriculation,
            "date_mise_en_circulation": v.date_mise_en_circulation,
        }
        for v in vehicules
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_add_vehicule(request):
    if request.method == 'POST':
        try:
 
            user = get_user_from_request(request)
            if not user:
                return JsonResponse({'error': 'Utilisateur non authentifié'}, status=401)

            data = json.loads(request.body.decode('utf-8'))
            marque = data['marque']
            modele = data['modele']
            immatriculation = data['immatriculation']
            print (immatriculation)
            date_mise_en_circulation = datetime.strptime(
                data['date_mise_en_circulation'], '%Y-%m-%d'
            ).date()
            print (user)
            vehicule = Vehicule.objects.create(
                proprietaire=user,
                marque=marque,
                modele=modele,
                immatriculation=immatriculation,
                date_mise_en_circulation=date_mise_en_circulation
            )
            print (date_mise_en_circulation)
            return JsonResponse({
                'message': 'Véhicule ajouté avec succès',
                'vehicule_id': vehicule.id
            }, status=201)

        except KeyError as e:
            return JsonResponse({'error': f"Champ manquant : {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
