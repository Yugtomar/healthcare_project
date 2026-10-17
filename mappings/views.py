from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import MappingSerializer


def user_mappings(user):
    """Mappings that belong to patients created by this user."""
    return PatientDoctorMapping.objects.filter(patient__created_by=user).select_related(
        "patient", "doctor"
    )


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer

    def get_queryset(self):
        return user_mappings(self.request.user)


class MappingDetailView(APIView):
    """
    The assignment uses the same URL shape for two things:
      GET    /api/mappings/<patient_id>/  -> doctors assigned to that patient
      DELETE /api/mappings/<id>/          -> remove a mapping
    GET treats the number as a patient id, DELETE treats it as a mapping id.
    """

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = user_mappings(request.user).filter(patient=patient)
        serializer = MappingSerializer(mappings, many=True, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, pk):
        mapping = get_object_or_404(user_mappings(request.user), pk=pk)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
