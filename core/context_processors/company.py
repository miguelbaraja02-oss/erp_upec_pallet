from companies.models import Company, CompanyUser, CompanyInvitation

def active_company(request):
    company_id = request.session.get("company_id")
    company = None
    company_user = None
    accessible_modules = []
    is_owner = False

    if company_id and request.user.is_authenticated:
        company = Company.objects.filter(id=company_id).first()
        
        if company:
            try:
                company_user = CompanyUser.objects.select_related('role').get(
                    user=request.user,
                    company=company,
                    is_active=True
                )
                is_owner = company_user.is_owner
                try:
                    accessible_modules = list(company_user.get_accessible_modules())
                except Exception:
                    # Si la tabla de módulos no existe aún
                    accessible_modules = []
            except CompanyUser.DoesNotExist:
                pass
            except Exception:
                # Si la tabla de roles no existe aún (migraciones pendientes)
                try:
                    company_user = CompanyUser.objects.get(
                        user=request.user,
                        company=company,
                        is_active=True
                    )
                    is_owner = company_user.is_owner
                except CompanyUser.DoesNotExist:
                    pass
                except Exception:
                    pass

    return {
        "active_company": company,
        "company_user": company_user,
        "is_company_owner": is_owner,
        "accessible_modules": accessible_modules,
    }


def pending_invitations(request):
    """
    Context processor para incluir las invitaciones pendientes en todas las páginas.
    Esto permite mostrar notificaciones en la navbar.
    """
    pending_invitations = []
    pending_invitations_count = 0
    
    if request.user.is_authenticated:
        try:
            pending_invitations = list(CompanyInvitation.get_pending_for_user(request.user))
            pending_invitations_count = len(pending_invitations)
        except Exception:
            # Si la tabla no existe aún
            pass
    
    return {
        "pending_invitations": pending_invitations,
        "pending_invitations_count": pending_invitations_count,
    }
