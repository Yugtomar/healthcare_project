from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Doctor
from .permissions import IsCreatorOrReadOnly
from .serializers import DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]
