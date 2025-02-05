from django.shortcuts import render, redirect
from .models import Cliente
from .form import ClienteForm, AccountAuthenticationForm

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.core.paginator import Paginator
from .filters import ClienteFilter
from django.db.models import Sum
import locale

import base64
from django.core.files.base import ContentFile

def login_view(request):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect('cliente')
    
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect('cliente')
    
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'cliente/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def cliente(request):
    # list_clientes = Cliente.objects.all()
    list_clientes = Cliente.objects.order_by('-data_criacao')
    myFilter = ClienteFilter(request.GET, queryset=list_clientes)
    list_clientes = myFilter.qs
    paginator = Paginator(list_clientes, 8)
    page = request.GET.get('page')
    list_clientes = paginator.get_page(page)
    return render(request, 'cliente/cliente.html', {'clientes': list_clientes, 'myFilter': myFilter})

@login_required(login_url='login')
def detalhe(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    return render(request, 'cliente/detalhe.html', {'cliente': cliente})

@login_required(login_url='login')
def form(request):
    data = {}
    data['form'] = ClienteForm()
    return render(request, 'cliente/form.html', data)

@login_required(login_url='login')
def create(request):
    if request.method == 'POST':
        webimg = request.POST.get('webimg')  # Obtém o valor Base64 do input hidden
        if webimg:
            # Decodifica o Base64 em um arquivo
            format, imgstr = webimg.split(';base64,')
            ext = format.split('/')[-1]
            img_data = ContentFile(base64.b64decode(imgstr), name=f"uploaded_image.{ext}")

            # Atualiza o request.FILES para incluir a imagem decodificada
            request.FILES['comprovante_entrega'] = img_data  # 'image' deve ser o nome do campo no seu modelo/formulário

        # Processa o formulário normalmente
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Pedido cadastrado com sucesso.')
            return redirect('cliente')
    else:
        form = ClienteForm()

@login_required(login_url='login')
def edit(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    form = ClienteForm(instance=cliente)
    return render(request, 'cliente/form.html', {'cliente': cliente, 'form': form})

@login_required(login_url='login')
def update(request, pk):
    cliente = Cliente.objects.get(pk=pk)

    if request.method == 'POST':
        webimg = request.POST.get('webimg')  # Captura o valor Base64 do input hidden (se existir)
        if webimg:
            # Decodifica o Base64 e cria um arquivo
            format, imgstr = webimg.split(';base64,')
            ext = format.split('/')[-1]
            img_data = ContentFile(base64.b64decode(imgstr), name=f"updated_image.{ext}")
            
            # Atualiza o campo de imagem do cliente
            cliente.comprovante_entrega = img_data
            cliente.save()
            messages.add_message(request, messages.SUCCESS, 'Imagem atualizada com sucesso.')
            return redirect('cliente')

        # Processa o restante do formulário
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Pedido atualizado com sucesso.')
            return redirect('cliente')

    # Requisição GET ou outros fluxos que não retornam nada
    form = ClienteForm(instance=cliente)
    return render(request, 'cliente/form.html', {'cliente': cliente, 'form': form})

@login_required(login_url='login')
def delete(request, pk):
    cliente = Cliente.objects.get(pk=pk)
    cliente.delete()
    messages.add_message(request, messages.ERROR, 'Pedido excluido com sucesso.')
    return redirect('cliente')

@login_required(login_url='login')
def dashboard(request):

    number_empenhos = Cliente.objects.count()

    # valor total
    valor = Cliente.objects.values_list('valor', flat=True)

    valor = list(valor)

    a = [i.replace('.', '') for i in valor]

    aa = [i.replace(',', '.') for i in a]

    b = [float(i) for i in aa]

    soma = 0

    for val in b:
        soma += val

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    soma = locale.currency(soma, grouping=True, symbol=None)

    return render(request, 'cliente/dashboard.html', {'nempenhos': number_empenhos, 'valor': soma})