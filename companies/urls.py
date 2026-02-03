from django.urls import path
from .views.create_company import create_company
from .views.edit_companies import edit_company
from .views.deactivate_company import deactivate_company
from .views.roles import (
    role_list,
    role_create,
    role_edit,
    role_delete,
    role_permissions,
    role_permissions_save,
    role_toggle_permission,
)
from .views.invitations import (
    invitation_list,
    invitation_create,
    search_users,
    invitation_cancel,
    my_invitations,
    invitation_accept,
    invitation_reject,
    pending_invitations_count,
)
from .views.company_users import (
    company_users_list,
    toggle_user_status,
    assign_role,
    remove_user,
    search_company_users,
)

app_name = "companies"

urlpatterns = [
    path("create/", create_company, name="create"),
    path("edit/<int:company_id>/", edit_company, name="edit_company"),
    
    path("deactivate/<int:company_id>/",deactivate_company,name="deactivate"
    ),
    
    # URLs para gestión de roles
    path("roles/", role_list, name="role_list"),
    path("roles/create/", role_create, name="role_create"),
    path("roles/<int:role_id>/edit/", role_edit, name="role_edit"),
    path("roles/<int:role_id>/delete/", role_delete, name="role_delete"),
    path("roles/<int:role_id>/permissions/", role_permissions, name="role_permissions"),
    path("roles/<int:role_id>/permissions/save/", role_permissions_save, name="role_permissions_save"),
    path("roles/<int:role_id>/toggle-permission/", role_toggle_permission, name="role_toggle_permission"),
    
    # URLs para gestión de invitaciones (desde la empresa)
    path("invitations/", invitation_list, name="invitation_list"),
    path("invitations/create/", invitation_create, name="invitation_create"),
    path("invitations/search-users/", search_users, name="search_users"),
    path("invitations/<int:invitation_id>/cancel/", invitation_cancel, name="invitation_cancel"),
    
    # URLs para el usuario invitado
    path("my-invitations/", my_invitations, name="my_invitations"),
    path("invitations/<int:invitation_id>/accept/", invitation_accept, name="invitation_accept"),
    path("invitations/<int:invitation_id>/reject/", invitation_reject, name="invitation_reject"),
    path("invitations/pending-count/", pending_invitations_count, name="pending_invitations_count"),
    
    # URLs para gestión de usuarios de la empresa
    path("users/", company_users_list, name="company_users_list"),
    path("users/<int:user_id>/toggle-status/", toggle_user_status, name="toggle_user_status"),
    path("users/<int:user_id>/assign-role/", assign_role, name="assign_role"),
    path("users/<int:user_id>/remove/", remove_user, name="remove_user"),
    path("users/search/", search_company_users, name="search_company_users"),
]
