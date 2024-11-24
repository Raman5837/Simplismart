from django.db.models import TextChoices


class UserRole(TextChoices):
    ADMIN = "ADMIN", "Admin Role"
    VIEWER = "VIEWER", "Viewer Role"
    DEVELOPER = "DEVELOPER", "Developer Role"


class DeploymentStatus(TextChoices):
    FAILED = "FAILED", "Failed"
    QUEUED = "QUEUED", "In Queue"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Deployment Completed"
