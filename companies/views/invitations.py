from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Company, CompanyUser, CompanyInvitation


def get_company_and_validate_owner(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return None, None, redirect('companies:select')

    company = get_object_or_404(Company, id=company_id, is_active=True)

    try:
        company_user = CompanyUser.objects.get(
            user=request.user,
            company=company,
            is_active=True
        )
    except CompanyUser.DoesNotExist:
        return None, None, redirect('companies:select')

    if not company_user.is_owner:
        messages.error(request, 'Solo el dueño puede gestionar las invitaciones.')
        return None, None, redirect('core:dashboard')

    return company, company_user, None


@login_required
def invitation_list(request):
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error

    invitations = CompanyInvitation.objects.filter(company=company).select_related('invited_user', 'invited_by')
    
    # Contar por estado
    pending_count = invitations.filter(status='pending').count()
    accepted_count = invitations.filter(status='accepted').count()
    rejected_count = invitations.filter(status='rejected').count()
    cancelled_count = invitations.filter(status='cancelled').count()

    context = {
        'company': company,
        'invitations': invitations,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'cancelled_count': cancelled_count,
    }
    return render(request, 'companies/invitations/invitation_list.html', context)


@login_required
def invitation_create(request):
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        message = request.POST.get('message', '').strip()

        User = get_user_model()
        try:
            invited_user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Usuario no encontrado.')
            return redirect('companies:invitation_list')

        can_invite, reason = CompanyInvitation.can_invite_user(company, invited_user)
        if not can_invite:
            messages.error(request, reason or 'No se puede invitar a este usuario.')
            return redirect('companies:invitation_list')

        inv = CompanyInvitation.objects.create(
            company=company,
            invited_user=invited_user,
            invited_by=request.user,
            message=message,
            status='pending',
        )
        messages.success(request, f'Invitación enviada a {invited_user.username}.')
        return redirect('companies:invitation_list')

    # For GET, render a simple selection page
    users = get_user_model().objects.exclude(id=request.user.id)[:50]
    return render(request, 'companies/invitations/invitation_create.html', {'company': company, 'users': users})


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    
    # Solo buscar si hay query de al menos 2 caracteres
    if len(query) < 2:
        return JsonResponse({'success': True, 'users': []})
    
    User = get_user_model()
    from django.db.models import Q
    
    # Buscar por username o email
    qs = User.objects.filter(
        Q(username__icontains=query) | 
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:20]

    users = []
    company_id = request.session.get('company_id')
    company = None
    if company_id:
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            company = None

    for u in qs:
        is_member = False
        has_pending = False
        can_invite = True
        
        if company:
            is_member = CompanyUser.objects.filter(company=company, user=u).exists()
            has_pending = CompanyInvitation.objects.filter(company=company, invited_user=u, status='pending').exists()
            can_invite = not is_member and not has_pending
        
        # Obtener avatar si existe
        avatar_url = None
        if hasattr(u, 'profile') and u.profile and u.profile.avatar:
            avatar_url = u.profile.avatar.url

        users.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'full_name': f"{u.first_name} {u.last_name}".strip() or u.username,
            'avatar': avatar_url,
            'is_member': is_member,
            'has_pending': has_pending,
            'can_invite': can_invite,
        })

    return JsonResponse({'success': True, 'users': users})


@login_required
def invitation_cancel(request, invitation_id):
    company, company_user, error = get_company_and_validate_owner(request)
    if error:
        return error

    invitation = get_object_or_404(CompanyInvitation, id=invitation_id, company=company)
    if invitation.status != 'pending':
        messages.error(request, 'La invitación ya no está pendiente.')
    else:
        invitation.cancel()
        messages.success(request, 'Invitación cancelada.')

    return redirect('companies:invitation_list')


@login_required
def my_invitations(request):
    invitations = CompanyInvitation.get_pending_for_user(request.user)
    return render(request, 'companies/invitations/my_invitations.html', {'invitations': invitations})


@login_required
def invitation_accept(request, invitation_id):
    invitation = get_object_or_404(CompanyInvitation, id=invitation_id, invited_user=request.user)
    if invitation.accept():
        messages.success(request, 'Invitación aceptada. Ahora perteneces a la empresa.')
    else:
        messages.error(request, 'No se pudo aceptar la invitación.')
    return redirect('companies:my_invitations')


@login_required
def invitation_reject(request, invitation_id):
    invitation = get_object_or_404(CompanyInvitation, id=invitation_id, invited_user=request.user)
    if invitation.reject():
        messages.success(request, 'Invitación rechazada.')
    else:
        messages.error(request, 'No se pudo rechazar la invitación.')
    return redirect('companies:my_invitations')


@login_required
def pending_invitations_count(request):
    count = CompanyInvitation.get_pending_for_user(request.user).count()
    return JsonResponse({'success': True, 'pending_count': count})
