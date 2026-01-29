from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Candidate
from ai_engine.tasks import process_audit_task

class GHLWebhookView(APIView):
    def post(self, request):
        data = request.data
        
        ghl_contact_id = data.get('contact_id')
        cv_text = data.get('cv_text')
        
        if not ghl_contact_id or not cv_text:
            return Response(
                {"error": "Missing required fields: contact_id and cv_text are mandatory."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract other fields with defaults or None
        first_name = data.get('first_name', 'Unknown')
        email = data.get('email', 'unknown@example.com')
        target_region = data.get('target_region', 'Ontario')
        profession = data.get('profession', 'Doctor')

        # Update or create the candidate
        candidate, created = Candidate.objects.update_or_create(
            ghl_contact_id=ghl_contact_id,
            defaults={
                'first_name': first_name,
                'email': email,
                'resume_text': cv_text,
                'target_region': target_region,
                'profession': profession
            }
        )

        # Trigger the async audit task
        process_audit_task.delay(candidate.id)

        return Response(
            {
                "status": "processing_started", 
                "candidate_id": candidate.id
            }, 
            status=status.HTTP_200_OK
        )
