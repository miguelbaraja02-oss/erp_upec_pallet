from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from companies.models import CompanyUser, Company

@login_required
def welcome(request):
    companies = CompanyUser.objects.filter(
        user=request.user,
        is_active=True,
        company__is_active=True
    ).select_related("company")

    if request.method == "POST":
        company_id = request.POST.get("company_id")
        if company_id:
            request.session["company_id"] = int(company_id)
            return redirect("core:dashboard")

    return render(request, "home/welcome.html", {
        "companies": companies
    })
    