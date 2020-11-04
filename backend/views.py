import json

from django.shortcuts import render
from django.http import HttpResponse
from .forms import ProjectForm


# Create your views here.
def add_product(request):
    if request.method == 'POST':
        form = ProjectForm(json.loads(bytes.decode(request.body)))
        if form.is_valid():
            print(form)
    return HttpResponse('ok')
