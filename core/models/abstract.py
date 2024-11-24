from datetime import datetime

from django.db import models


class AbstractModel(models.Model):
    """
    Abstract Model
    """

    id: int = models.AutoField(primary_key=True)
    is_deleted: bool = models.BooleanField(default=False)
    modified_at: datetime = models.DateTimeField(auto_now=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["created_at", "is_deleted"]),
        ]

    def delete(self, using=None, keep_parents=False) -> None:
        """
        Override the delete method for soft deletion.
        """

        _ = using, keep_parents

        self.is_deleted = True
        self.save()

    def restore(self) -> None:
        """
        Restore the soft-deleted object.
        """

        self.is_deleted = False
        self.save()
