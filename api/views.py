from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Candidate
from ai_engine.tasks import audit_candidate_cv

class GHLWebhookView(APIView):
    def post(self, request):
        data = request.data
        contact_id = data.get('contact_id')
        cv_text = data.get('cv_text')
        target_region = data.get('target_region')

        if not contact_id or not cv_text:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        candidate, created = Candidate.objects.update_or_create(
            contact_id=contact_id,
            defaults={'cv_text': cv_text, 'target_region': target_region}
        )

        # Trigger async task
        audit_candidate_cv.delay(candidate.id)

        return Response({"status": "received", "candidate_id": candidate.id}, status=status.HTTP_200_OK)
