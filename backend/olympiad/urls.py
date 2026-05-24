from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet,
    LevelViewSet,
    StudentViewSet,
    QuestionViewSet,
    ResultViewSet,
    ExamStartAPIView,
    ExamSubmitAPIView,
    MentalProgressAPIView,
    PublicResultLookupAPIView,
    PublicResultsListAPIView,
)

router = DefaultRouter()
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('levels', LevelViewSet, basename='levels')
router.register('students', StudentViewSet, basename='students')
router.register('questions', QuestionViewSet, basename='questions')
router.register('results', ResultViewSet, basename='results')

urlpatterns = [
    path('', include(router.urls)),
    path('exam/start/', ExamStartAPIView.as_view(), name='exam-start'),
    path('exam/submit/', ExamSubmitAPIView.as_view(), name='exam-submit'),
    path('exam/mental-progress/', MentalProgressAPIView.as_view(), name='exam-mental-progress'),
    path('exam/result/', PublicResultLookupAPIView.as_view(), name='exam-result'),
    path('exam/public-results/', PublicResultsListAPIView.as_view(), name='exam-public-results'),
]
