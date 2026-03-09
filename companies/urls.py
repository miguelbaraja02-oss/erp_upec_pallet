from .views.users import list_company_users, deactivate_company_user, activate_company_user
from .views.overview import dashboard, overview
from .views.select_company import select_company
from django.urls import path

from .views.create_company import create_company
from .views.edit_companies import edit_company
from .views.deactivate_company import deactivate_company
from .views.roles import list_roles, create_role, edit_role, delete_role
from .views.assign_role import assign_role
from .views.invitations import invite_user, manage_invitations, respond_invitation, search_users

app_name = "companies"

urlpatterns = [
    path("select/<int:company_id>/", select_company, name="select_company"),
    path("create/", create_company, name="create"),
    path("edit/<int:company_id>/", edit_company, name="edit_company"),
    path("deactivate/<int:company_id>/", deactivate_company, name="deactivate"),
    path("roles/", list_roles, name="list_roles"),
    path("roles/create/", create_role, name="create_role"),
    path("roles/edit/<int:role_id>/", edit_role, name="edit_role"),
    path("roles/delete/<int:role_id>/", delete_role, name="delete_role"),

    # Vista general de la empresa
    path("<int:company_id>/overview/", overview, name="overview"),
    path("dashboard/", dashboard, name="dashboard"),

    # Invitaciones
    path("<int:company_id>/invite/", invite_user, name="invite_user"),
    path("invitations/", manage_invitations, name="manage_invitations"),
    path("invitations/<int:invitation_id>/<str:action>/", respond_invitation, name="respond_invitation"),

    # Usuarios de empresa
    path("users/", list_company_users, name="list_company_users"),
    path("users/deactivate/<int:user_id>/", deactivate_company_user, name="deactivate_company_user"),
    path("users/activate/<int:user_id>/", activate_company_user, name="activate_company_user"),
    path("roles/assign/", assign_role, name="assign_role"),
    path("<int:company_id>/search_users/", search_users, name="search_users"),
]
