from django.shortcuts import render, redirect
from store.forms import AlmacenForm
from store.models import Almacen
from companies.models import Company, CompanyUser

def vista_almacenes(request):
    form = AlmacenForm()
    user = request.user
    active_company = None
    if user.is_authenticated:
        company_user = CompanyUser.objects.filter(user=user, is_active=True).first()
        if company_user:
            active_company = company_user.company
    if active_company:
        almacenes = Almacen.objects.filter(company=active_company, is_active=True)
    else:
        almacenes = Almacen.objects.none()
    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            almacen = form.save(commit=False)
            if not hasattr(almacen, 'descripcion') or almacen.descripcion is None:
                almacen.descripcion = ''
            if active_company:
                almacen.company = active_company
            else:
                almacen.company = Company.objects.first()
            almacen.save()
            return redirect('warehouses_list')
    mostrar_formulario = almacenes.count() == 0
    return render(request, "overview/overview.html", {"form": form, "almacenes": almacenes, "mostrar_formulario": mostrar_formulario})
