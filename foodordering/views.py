from django.http import JsonResponse

def home(request):
    data = {
        "message": "Home Page"
    }
    return JsonResponse(data)