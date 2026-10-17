from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient

User = get_user_model()


class PortalAuthenticationTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("portal:dashboard"))

        self.assertRedirects(
            response, f"{reverse('portal:login')}?next={reverse('portal:dashboard')}"
        )

    def test_signed_in_user_sees_workspace_dashboard(self):
        user = User.objects.create_user(
            username="dashboard@example.com",
            email="dashboard@example.com",
            password="Tide!Glass83Horizon",
            first_name="Maya",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("portal:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Good to see you, Maya")
        self.assertContains(response, "Patients in your care")
        self.assertContains(response, "Care teams")

    def test_registration_creates_account_and_signs_user_in(self):
        response = self.client.post(
            reverse("portal:register"),
            {
                "name": "Maya Chen",
                "email": "Maya@example.com",
                "password1": "Tide!Glass83Horizon",
                "password2": "Tide!Glass83Horizon",
            },
        )

        self.assertRedirects(response, reverse("portal:dashboard"))
        self.assertTrue(
            User.objects.filter(username="maya@example.com", email="maya@example.com").exists()
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_duplicate_registration_shows_error(self):
        User.objects.create_user(
            username="maya@example.com",
            email="maya@example.com",
            password="Tide!Glass83Horizon",
        )

        response = self.client.post(
            reverse("portal:register"),
            {
                "name": "Maya Chen",
                "email": "MAYA@example.com",
                "password1": "Tide!Glass83Horizon",
                "password2": "Tide!Glass83Horizon",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(User.objects.count(), 1)

    def test_login_uses_email_and_opens_dashboard(self):
        User.objects.create_user(
            username="maya@example.com",
            email="maya@example.com",
            password="Tide!Glass83Horizon",
        )

        response = self.client.post(
            reverse("portal:login"),
            {"email": "MAYA@example.com", "password": "Tide!Glass83Horizon"},
        )

        self.assertRedirects(response, reverse("portal:dashboard"))
        self.assertIn("_auth_user_id", self.client.session)


class PatientWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="clinician@example.com",
            email="clinician@example.com",
            password="Tide!Glass83Horizon",
            first_name="Alex",
        )
        self.client.force_login(self.user)

    def test_create_search_and_edit_patient(self):
        response = self.client.post(
            reverse("portal:patient-create"),
            {
                "name": "Jordan Lee",
                "age": 38,
                "gender": "O",
                "phone": "5550123",
                "address": "12 Garden Road",
                "medical_history": "Seasonal allergies",
            },
        )

        self.assertRedirects(response, reverse("portal:patients"))
        patient = Patient.objects.get(name="Jordan Lee")
        self.assertEqual(patient.created_by, self.user)

        response = self.client.get(reverse("portal:patients"), {"q": "Jordan"})
        self.assertContains(response, "Jordan Lee")

        response = self.client.post(
            reverse("portal:patient-update", args=[patient.pk]),
            {
                "name": "Jordan Lee",
                "age": 39,
                "gender": "O",
                "phone": "5550123",
                "address": "12 Garden Road",
                "medical_history": "Seasonal allergies",
            },
        )
        self.assertRedirects(response, reverse("portal:patients"))
        patient.refresh_from_db()
        self.assertEqual(patient.age, 39)

    def test_patient_records_are_private_and_delete_requires_post(self):
        another_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="Tide!Glass83Horizon",
        )
        patient = Patient.objects.create(
            created_by=another_user,
            name="Private Patient",
            age=41,
            gender="F",
        )

        self.assertEqual(
            self.client.get(reverse("portal:patient-update", args=[patient.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("portal:patient-delete", args=[patient.pk])).status_code,
            405,
        )
        self.assertTrue(Patient.objects.filter(pk=patient.pk).exists())

    def test_patient_age_is_validated(self):
        response = self.client.post(
            reverse("portal:patient-create"),
            {"name": "Out of range", "age": 151, "gender": "F"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "realistic age")
        self.assertFalse(Patient.objects.filter(name="Out of range").exists())


class DoctorAndAssignmentWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="doctor-owner@example.com",
            email="doctor-owner@example.com",
            password="Tide!Glass83Horizon",
        )
        self.client.force_login(self.user)
        self.patient = Patient.objects.create(
            created_by=self.user,
            name="Taylor Morgan",
            age=29,
            gender="F",
        )
        self.doctor = Doctor.objects.create(
            created_by=self.user,
            name="Avery Singh",
            specialization="Cardiology",
            email="avery@example.com",
            experience_years=8,
        )

    def test_doctor_create_and_creator_only_edit(self):
        response = self.client.post(
            reverse("portal:doctor-create"),
            {
                "name": "Sam Patel",
                "specialization": "Neurology",
                "email": "sam@example.com",
                "phone": "",
                "experience_years": 5,
            },
        )
        self.assertRedirects(response, reverse("portal:doctors"))
        self.assertTrue(Doctor.objects.filter(email="sam@example.com").exists())

        another_user = User.objects.create_user(
            username="another@example.com",
            email="another@example.com",
            password="Tide!Glass83Horizon",
        )
        self.client.force_login(another_user)
        self.assertEqual(
            self.client.get(reverse("portal:doctor-update", args=[self.doctor.pk])).status_code,
            404,
        )

    def test_assignment_and_duplicate_validation(self):
        payload = {"patient": self.patient.pk, "doctor": self.doctor.pk}
        response = self.client.post(reverse("portal:assignment-create"), payload)
        self.assertRedirects(response, reverse("portal:assignments"))
        self.assertTrue(
            PatientDoctorMapping.objects.filter(
                patient=self.patient, doctor=self.doctor
            ).exists()
        )

        response = self.client.post(reverse("portal:assignment-create"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already assigned")
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)

    def test_assignment_can_only_target_own_patients(self):
        another_user = User.objects.create_user(
            username="patient-owner@example.com",
            email="patient-owner@example.com",
            password="Tide!Glass83Horizon",
        )
        private_patient = Patient.objects.create(
            created_by=another_user,
            name="Not My Patient",
            age=34,
            gender="M",
        )

        response = self.client.post(
            reverse("portal:assignment-create"),
            {"patient": private_patient.pk, "doctor": self.doctor.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            PatientDoctorMapping.objects.filter(patient=private_patient).exists()
        )
