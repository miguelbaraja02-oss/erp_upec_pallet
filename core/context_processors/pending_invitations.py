from companies.models import Invitation

def pending_invitations(request):
    if request.user.is_authenticated:
        count = Invitation.objects.filter(invited_user=request.user, status="pending").count()
        return {"pending_invitations_count": count}
    return {"pending_invitations_count": 0}
