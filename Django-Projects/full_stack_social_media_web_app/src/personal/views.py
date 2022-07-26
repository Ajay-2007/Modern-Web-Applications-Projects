from django.shortcuts import render

# Create your views here.
def home_screen_view(request, *args, **kwargs):
    context = {}
    context['my_name'] = "mitch"

    return render(request, "personal/home.html", context)