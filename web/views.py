from django.shortcuts import render


def home(request):
    return render(request, "home.html", {"loop": range(0, 20)})
