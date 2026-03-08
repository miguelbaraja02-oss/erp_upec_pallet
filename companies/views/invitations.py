from django.contrib.auth.decorators import login_required
from companies.decorators import company_admin_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from companies.models import Company, CompanyUser, Invitation
from accounts.models import User
from django.views.decorators.http import require_GET

@login_required
@company_admin_required
def invite_user(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    # Solo administradores pueden invitar
    from companies.models import UserRole
    user_role = UserRole.objects.filter(user=request.user, company=company, role__name="Administrador").first()
    if not user_role:
        return HttpResponseForbidden("No tienes permisos para invitar usuarios a esta empresa.")

    # Filtrado por username o email
    query = request.GET.get("query", "")
    company_users = CompanyUser.objects.filter(company=company).values_list("user_id", flat=True)
    available_users = User.objects.exclude(id__in=company_users)
    if query:
        available_users = available_users.filter(
            username__icontains=query
        ) | available_users.filter(
            email__icontains=query
        )

    if request.method == "POST":
        username = request.POST.get("username")
        invited_user = User.objects.filter(username=username).first()
        if not invited_user:
            messages.error(request, "Usuario no encontrado.")
        else:
            existing_invite = Invitation.objects.filter(company=company, invited_user=invited_user).first()
            if existing_invite:
                if existing_invite.status in ["rejected", "cancelled"]:
                    existing_invite.status = "pending"
                    existing_invite.invited_by = request.user
                    existing_invite.save()
                    messages.success(request, f"Invitación reenviada a {invited_user.username}.")
                else:
                    messages.warning(request, "Ya existe una invitación pendiente o aceptada para este usuario.")
            else:
                Invitation.objects.create(
                    company=company,
                    invited_by=request.user,
                    invited_user=invited_user
                )
                messages.success(request, f"Invitación enviada a {invited_user.username}.")
        return redirect("companies:invite_user", company_id=company.id)

    context = {
        "company": company,
        "available_users": available_users,
        "invitations": Invitation.objects.filter(company=company),
        "query": query,
        "active_module": "invite",
    }
    return render(request, "companies/invitations/invite_user.html", context)

@login_required
def manage_invitations(request):
    # Invitaciones recibidas por el usuario
    invitations = Invitation.objects.filter(invited_user=request.user, status="pending")
    context = {"invitations": invitations}
    return render(request, "companies/invitations/manage_invitations.html", context)

@login_required
def respond_invitation(request, invitation_id, action):
    invitation = get_object_or_404(Invitation, id=invitation_id, invited_user=request.user)
    if invitation.status != "pending":
        return JsonResponse({"error": "La invitación ya fue respondida."}, status=400)
    if action == "accept":
        invitation.status = "accepted"
        invitation.save()
        # Crear roles por defecto si no existen
        from companies.models import Role, UserRole
        admin_role, _ = Role.objects.get_or_create(name="Administrador")
        employee_role, _ = Role.objects.get_or_create(name="Empleado")
        # Agregar usuario a la empresa
        company_user = CompanyUser.objects.create(user=request.user, company=invitation.company)
        # Asignar rol Empleado por defecto
        UserRole.objects.create(user=request.user, role=employee_role)
        messages.success(request, f"Te has unido a la empresa {invitation.company.name}.")
    elif action == "reject":
        invitation.status = "rejected"
        invitation.save()
        messages.info(request, "Has rechazado la invitación.")
    else:
        return JsonResponse({"error": "Acción inválida."}, status=400)
    return redirect("core:welcome")

@require_GET
@login_required
@company_admin_required
def search_users(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    query = request.GET.get("query", "")
    # Solo usuarios que NO están en la empresa
    company_users = CompanyUser.objects.filter(company=company).values_list("user_id", flat=True)
    available_users = User.objects.exclude(id__in=company_users)
    if query:
        available_users = available_users.filter(
            username__icontains=query
        ) | available_users.filter(
            email__icontains=query
        )
    users = list(available_users.values("username", "email")[:10])
    return JsonResponse({"users": users})
