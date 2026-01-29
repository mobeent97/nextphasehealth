from django.db import models

class Candidate(models.Model):
    ghl_contact_id = models.CharField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    email = models.EmailField()
    resume_text = models.TextField()
    target_region = models.CharField(max_length=255, default='Ontario')
    profession = models.CharField(max_length=255, default='Doctor')
    readiness_score = models.IntegerField(null=True, blank=True)
    is_fast_track_eligible = models.BooleanField(default=False)
    audit_report_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        score = self.readiness_score if self.readiness_score is not None else "N/A"
        return f"{self.first_name} ({self.email}) - Score: {score}"
