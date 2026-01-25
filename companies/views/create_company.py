from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import CompanyCreateForm
from ..models import CompanyUser

@login_required
def create_company(request):
    if request.method == "POST":
        form = CompanyCreateForm(request.POST)

        if form.is_valid():
            company = form.save()

            CompanyUser.objects.create(
                user=request.user,
                company=company,
                is_owner=True
            )

            return redirect("core:welcome")
    else:
        form = CompanyCreateForm()

    return render(request, "companies/create_company.html", {"form": form})
