from django.contrib import admin
from .models import Company, CompanyUser, Module, PermissionType, Role, RolePermission, CompanyInvitation


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ruc', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'ruc')


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role', 'is_owner', 'is_active', 'created_at')
    list_filter = ('is_owner', 'is_active', 'company')
    search_fields = ('user__username', 'user__email', 'company__name')
    raw_id_fields = ('user', 'company', 'role')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'icon', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    ordering = ('order', 'name')


@admin.register(PermissionType)
class PermissionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'company')
    search_fields = ('name', 'company__name')
    raw_id_fields = ('company',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module', 'permission_type')
    list_filter = ('role__company', 'module', 'permission_type')
    search_fields = ('role__name', 'module__name')
    raw_id_fields = ('role', 'module', 'permission_type')


@admin.register(CompanyInvitation)
class CompanyInvitationAdmin(admin.ModelAdmin):
    list_display = ('invited_user', 'company', 'invited_by', 'status', 'created_at', 'responded_at')
    list_filter = ('status', 'company', 'created_at')
    search_fields = ('invited_user__username', 'invited_user__email', 'company__name', 'invited_by__username')
    raw_id_fields = ('company', 'invited_user', 'invited_by')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')
