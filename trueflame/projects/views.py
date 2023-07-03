# from django.shortcuts import render
from django.views.generic.list import ListView


# from .models import Structure

# import for using mixins for class-based views
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

# import for restricting access to class-based views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# formsets
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

# adding content
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Content, Structure, DiverseContent

# braces for reordeing modules
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

# displaying Projects
from django.db.models import Count
from .models import Project
from django.views.generic.detail import DetailView

# Your OwnerMixin class can be used for views that interact
# with any other model that contains an owner attribute


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerProjectMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    """
    inherits OwnerMixin and provides attributes for child views

    PermissionRequiredMixin checks that the user accessing the view has the
    permission specified in the permission_required attribute. Your views are
    now only accessible to users with proper permissions.
    """

    # model used for QuerySets; it is used by all views
    model = Structure
    # the fields of the model to build the model form of the CreateView and UpdateView views
    # fields = ["project", "title", "slug", "overview"]
    fields = ["title", "project", "owner", "overview", "slug", "page_hierarchy", "branding", "layout", "visual_elements", "navigation", "input_validation"]
    # Used by CreateView, UpdateView, and DeleteView to redirect the used after the form is successfully submitted or the object is deleted.
    success_url = reverse_lazy("manage_project_list")


class OwnerProjectEditMixin(OwnerProjectMixin, OwnerEditMixin):
    """
    template used for the CreateView and UpdateView views.
    """

    template_name = "projects/manage/project/form.html"


# class ManageProjectListView(ListView):
class ManageProjectListView(OwnerProjectEditMixin, ListView):
    """
    Inherits from Django's generic ListView.
    It overrides the get_queryset() method of the view
    to retrieve only projects created by current user.
    Is recommended to use mixins for providing specific
    behavior for several class-based views.

    Lists. the projects created by the user. It inherits
    from OwnerProjectMixin and ListView. It defines a
    specific template_name attribute for a template
    to list projects
    """

    # model = Project
    template_name = "projects/manage/project/list.html"
    permission_required = "projects.view_project"

    # def get_queryset(self):
    #    qs = super().get_queryset()
    #    return qs.filter(owner=self.request.user)


class ProjectCreateView(OwnerProjectEditMixin, CreateView):
    permission_required = "projects.add_project"


class ProjectUpdateView(OwnerProjectEditMixin, UpdateView):
    permission_required = "projects.change_project"


class ProjectDeleteView(OwnerProjectMixin, DeleteView):
    template_name = "projects/manage/project/delete.html"
    permission_required = "projects.delete_project"




class ProjectModuleUpdateView(TemplateResponseMixin, View):
    """
    This view handles the formset to add, update, and delete content
    for a specific structure
    """

    template_name = "projects/manage/module/formset.html"
    project = None

    def get_formset(self, data=None):
        """Avoid repeating the code to build the formset.
        Create a ModuleFormSet object for the given structure
        with obtional data."""
        return ModuleFormSet(instance=self.project, data=data)

    def dispatch(self, request, pk):
        self.project = get_object_or_404(Structure, id=pk, owner=request.user)

        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({"structure": self.project, "formset": formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("manage_project_list")
        return self.render_to_response({"structure": self.project, "formset": formset})

class ContentsCreateUpdateView(TemplateResponseMixin, View):
    '''Structure content '''
    content = None
    model = None
    obj = None
    template_name = 'projects/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='projects', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner','order','created','updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, content_id, model_name, id=None):
        self.content = get_object_or_404(Content, id=content_id, structure__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, content_id, model_name, id)

    def get(self, request, content_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})
    
    def post(self, request, content_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                DiverseContent.objects.create(content=self.content, item=obj)
            return redirect('module_content_list', self.content.id)
        return self.render_to_response({'form': form, 'object': self.obj})

class ContentsDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, content__structure__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ContentContentsListView(TemplateResponseMixin, View):
    template_name = 'projects/manage/module/content_list.html'

    def get(self, request, content_id):
        content = get_object_or_404(Content, id=content_id, structure__owner=request.user)
        return self.render_to_response({'content': content})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, structure__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentsOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Contents.objects.filter(id=id, content__structure__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class StructureListView(TemplateResponseMixin, View):
    model = Structure
    template_name = 'projects/project/list.html'

    def get(self, request, project=None):
        projects = Project.objects.annotate(
            total_structures=Count('structures'))
        structures = Structure.objects.annotate(
            total_contents=Count('contents'))
        
        if project:
            project = get_object_or_404(Project, slug=project)
            structures = structures.filter(project=project)
        return self.render_to_response({'projects': projects,
                                        'project': project, 
                                        'structures': structures})  

class StructureDetailView(DetailView):
    model = Structure
    template_name = 'projects/project/detail.html'