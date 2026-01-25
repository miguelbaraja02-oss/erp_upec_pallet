from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import CompanyUpdateForm
from ..models import Company, CompanyUser

@login_required
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    get_object_or_404(
        CompanyUser,
        user=request.user,
        company=company,
        is_owner=True
    )

    if request.method == "POST":
        form = CompanyUpdateForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("core:welcome")
    else:
        form = CompanyUpdateForm(instance=company)

    return render(request, "companies/edit_companies.html", {"form": form})

