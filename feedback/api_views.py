from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from core.models import Table
from .models import Feedback
from .serializers import FeedbackSerializer


@api_view(['POST'])
def submit_feedback_api(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    rating = request.data.get('rating')
    if not rating:
        return Response({'error': 'Baho talab qilinadi'}, status=status.HTTP_400_BAD_REQUEST)
    
    feedback = Feedback.objects.create(
        table=table,
        rating=int(rating),
        comment=request.data.get('comment', ''),
        menu_item_name=request.data.get('menu_item_name', ''),
        is_anonymous=request.data.get('is_anonymous') is True or request.data.get('is_anonymous') == 'true',
    )
    
    serializer = FeedbackSerializer(feedback)
    return Response({'status': 'success', 'message': 'Fikr-mulohaza yuborildi', 'feedback': serializer.data})


@api_view(['GET'])
def feedback_list_api(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)
