from rest_framework import serializers

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "patient_name", "doctor", "doctor_name", "assigned_at")
        read_only_fields = ("id", "assigned_at")

    def validate_patient(self, patient):
        user = self.context["request"].user
        if patient.created_by != user:
            raise serializers.ValidationError("You can only assign doctors to your own patients.")
        return patient

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(
            patient=attrs["patient"], doctor=attrs["doctor"]
        ).exists():
            raise serializers.ValidationError("This doctor is already assigned to this patient.")
        return attrs
