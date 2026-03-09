from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from accounts.models import User
from companies.decorators import company_admin_required
from companies.models import Company, CompanyUser, Invitation


def _send_invitation_created_event(invitation):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    company = invitation.company
    group_name = f"invitations_user_{invitation.invited_user_id}"
    payload = {
        "type": "invitation.created",
        "invitation": {
            "id": invitation.id,
            "company_name": company.name,
            "company_logo_url": company.logo.url if company.logo else None,
            "invited_by_username": invitation.invited_by.username,
            "accept_url": reverse("companies:respond_invitation", args=[invitation.id, "accept"]),
            "reject_url": reverse("companies:respond_invitation", args=[invitation.id, "reject"]),
        },
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "invitation_created",
            "payload": payload,
        },
    )


def _send_company_invitation_status_event(invitation):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        "type": "invitation.status_updated",
        "invitation": {
            "id": invitation.id,
            "invited_user_username": invitation.invited_user.username,
            "invited_user_email": invitation.invited_user.email,
            "status": invitation.status,
            "status_display": invitation.get_status_display(),
        },
    }

    async_to_sync(channel_layer.group_send)(
        f"company_invitations_{invitation.company_id}",
        {
            "type": "invitation_status_updated",
            "payload": payload,
        },
    )


@login_required
@company_admin_required
def invite_user(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    from companies.models import UserRole

    user_role = UserRole.objects.filter(
        user=request.user,
        company=company,
        role__name="Administrador",
    ).first()
    if not user_role:
        return HttpResponseForbidden("No tienes permisos para invitar usuarios a esta empresa.")

    query = request.GET.get("query", "")
    company_users = CompanyUser.objects.filter(company=company).values_list("user_id", flat=True)
    available_users = User.objects.exclude(id__in=company_users)
    if query:
        available_users = available_users.filter(username__icontains=query) | available_users.filter(
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
                    _send_invitation_created_event(existing_invite)
                    _send_company_invitation_status_event(existing_invite)
                    messages.success(request, f"Invitacion reenviada a {invited_user.username}.")
                else:
                    messages.warning(request, "Ya existe una invitacion pendiente o aceptada para este usuario.")
            else:
                invitation = Invitation.objects.create(
                    company=company,
                    invited_by=request.user,
                    invited_user=invited_user,
                )
                _send_invitation_created_event(invitation)
                _send_company_invitation_status_event(invitation)
                messages.success(request, f"Invitacion enviada a {invited_user.username}.")

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
    invitations = Invitation.objects.filter(invited_user=request.user, status="pending")
    context = {"invitations": invitations}
    return render(request, "companies/invitations/manage_invitations.html", context)


@login_required
def respond_invitation(request, invitation_id, action):
    invitation = get_object_or_404(Invitation, id=invitation_id, invited_user=request.user)
    if invitation.status != "pending":
        return JsonResponse({"error": "La invitacion ya fue respondida."}, status=400)

    if action == "accept":
        invitation.status = "accepted"
        invitation.save()
        _send_company_invitation_status_event(invitation)

        from companies.models import Role, UserRole

        employee_role, _ = Role.objects.get_or_create(name="Empleado")
        CompanyUser.objects.get_or_create(user=request.user, company=invitation.company)
        UserRole.objects.update_or_create(
            user=request.user,
            company=invitation.company,
            defaults={"role": employee_role},
        )
        messages.success(request, f"Te has unido a la empresa {invitation.company.name}.")
    elif action == "reject":
        invitation.status = "rejected"
        invitation.save()
        _send_company_invitation_status_event(invitation)
        messages.info(request, "Has rechazado la invitacion.")
    else:
        return JsonResponse({"error": "Accion invalida."}, status=400)

    return redirect("core:welcome")


@require_GET
@login_required
@company_admin_required
def search_users(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    query = request.GET.get("query", "")

    company_users = CompanyUser.objects.filter(company=company).values_list("user_id", flat=True)
    available_users = User.objects.exclude(id__in=company_users)
    if query:
        available_users = available_users.filter(username__icontains=query) | available_users.filter(
            email__icontains=query
        )

    users = list(available_users.values("username", "email")[:10])
    return JsonResponse({"users": users})
