from companies.models import Invitation

def pending_invitations_list(request):
    if request.user.is_authenticated:
        invitations = Invitation.objects.filter(invited_user=request.user, status="pending")
        return {"pending_invitations_list": invitations}
    return {"pending_invitations_list": []}
