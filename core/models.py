from django.db import models

class Candidate(models.Model):
    contact_id = models.CharField(max_length=255, unique=True)
    cv_text = models.TextField()
    target_region = models.CharField(max_length=255)
    audit_results = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contact_id
