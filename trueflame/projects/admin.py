from django.contrib import admin
from .models import Project, Structure, Content


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


class ModuleInline(admin.StackedInline):
    model = Content


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "created"]
    list_filter = ["created", "project"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]
