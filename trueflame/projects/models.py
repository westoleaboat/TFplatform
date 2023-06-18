from django.db import models
from django.contrib.auth.models import User

# import for diverse content
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.fields import related

# import for adding ordering to content and diverse content objects
from .fields import OrderField


# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200)
    dev_roles = models.CharField(max_length=200)
    lang_pref = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Structure(models.Model):
    # Each project structure is divided into several content models.
    # Therefore, the Content model contains a ForeignKey field that
    # points to the Structure model.
    owner = models.ForeignKey(
        User, related_name="structures_created", on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        Project, related_name="structures", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)

    # Content organization
    content_organization = models.CharField(max_length=200)
    page_hierarchy = models.CharField(max_length=200)
    url_structure = models.CharField(max_length=200)

    # Design
    branding = models.CharField(max_length=200)
    layout = models.CharField(max_length=200)
    responsive_design = models.CharField(max_length=200)
    visual_elements = models.CharField(max_length=200)

    # UX/UI development
    navigation = models.CharField(max_length=200)
    user_flows = models.CharField(max_length=200)
    form_design = models.CharField(max_length=200)
    accessibility = models.CharField(max_length=200)

    # Security
    user_authentication = models.CharField(max_length=200)
    user_roles_permissions = models.CharField(max_length=200)
    input_validation = models.CharField(max_length=200)
    attack_protection = models.CharField(max_length=200)
    regular_updates = models.CharField(max_length=200)

    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    # automatically set
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class Content(models.Model):
    structure = models.ForeignKey(
        Structure, related_name="contents", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=["structure"])

   

    def __str__(self):
        return f"{self.order}. {self.title}"

    class Meta:
        ordering = ["order"]


class DiverseContent(models.Model):
    """
    This is the Diverse Content models. Content will vary ,
    so you define a ForeignKey field that points to the Content model.
    Also set up a generic relation to associate objects from different
    models that represent different types of content.
    """

    # diverse_content = models.ForeignKey(
    content = models.ForeignKey(
        Content, related_name="diverse_content", on_delete=models.CASCADE
    )
    # A ForeignKey field to the ContentType model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "video", "image", "file")},
    )
    # A PositiveIntegerField to store the primary key of the related object
    object_id = models.PositiveIntegerField()
    # A GenericForeignKey field to the related object combining the two previous fields
    item = GenericForeignKey("content_type", "object_id")
    # order = OrderField(blank=True, for_fields=["content"])
    order = OrderField(blank=True, for_fields=["content"])

    class Meta:
        ordering = ["order"]


class ItemBase(models.Model):
    # common fields for all types of content
    owner = models.ForeignKey(
        User, related_name="%(class)s_related", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Abstract Content model
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    """Store text content"""

    content = models.TextField()


class File(ItemBase):
    """Store files, such as PDFs"""

    file = models.FileField(upload_to="files")


class Image(ItemBase):
    """Store image files"""

    file = models.FileField(upload_to="images")


class Video(ItemBase):
    """Store videos. you use an URLField to provide a video URL in order to embed it"""

    url = models.URLField()
