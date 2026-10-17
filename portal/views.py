from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient

from .forms import (
    DoctorForm,
    MappingForm,
    PatientForm,
    PortalAuthenticationForm,
    RegistrationForm,
)


class PortalLoginView(LoginView):
    template_name = "portal/login.html"
    authentication_form = PortalAuthenticationForm
    redirect_authenticated_user = True
    next_page = reverse_lazy("portal:dashboard")


class PortalLogoutView(LogoutView):
    next_page = reverse_lazy("portal:login")


def register(request):
    if request.user.is_authenticated:
        return redirect("portal:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to CarePoint.")
        return redirect("portal:dashboard")
    return render(request, "portal/register.html", {"form": form})


@login_required
def dashboard(request):
    patients = Patient.objects.filter(created_by=request.user)
    context = {
        "patient_count": patients.count(),
        "doctor_count": Doctor.objects.count(),
        "assignment_count": PatientDoctorMapping.objects.filter(
            patient__created_by=request.user
        ).count(),
        "recent_patients": patients[:5],
        "recent_assignments": PatientDoctorMapping.objects.filter(
            patient__created_by=request.user
        ).select_related("patient", "doctor")[:5],
    }
    return render(request, "portal/dashboard.html", context)


@login_required
def patient_list(request):
    search = request.GET.get("q", "").strip()
    patients = Patient.objects.filter(created_by=request.user)
    if search:
        patients = patients.filter(
            Q(name__icontains=search) | Q(phone__icontains=search)
        )
    page = Paginator(patients, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "portal/patient_list.html",
        {"page": page, "search": search},
    )


@login_required
def patient_create(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save(commit=False)
        patient.created_by = request.user
        patient.save()
        messages.success(request, f"{patient.name} was added to your patients.")
        return redirect("portal:patients")
    return render(
        request,
        "portal/form_page.html",
        {
            "form": form,
            "title": "Add a patient",
            "description": "Add a patient record to your care list.",
            "cancel_url": "portal:patients",
            "submit_label": "Save patient",
        },
    )


@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{patient.name}'s record was updated.")
        return redirect("portal:patients")
    return render(
        request,
        "portal/form_page.html",
        {
            "form": form,
            "title": "Edit patient",
            "description": f"Update the record for {patient.name}.",
            "cancel_url": "portal:patients",
            "submit_label": "Save changes",
        },
    )


@login_required
@require_POST
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
    name = patient.name
    patient.delete()
    messages.success(request, f"{name}'s record was deleted.")
    return redirect("portal:patients")


@login_required
def doctor_list(request):
    doctors = Doctor.objects.select_related("created_by").all()
    search = request.GET.get("q", "").strip()
    if search:
        doctors = doctors.filter(
            Q(name__icontains=search)
            | Q(specialization__icontains=search)
            | Q(email__icontains=search)
        )
    page = Paginator(doctors, 10).get_page(request.GET.get("page"))
    return render(request, "portal/doctor_list.html", {"page": page, "search": search})


@login_required
def doctor_create(request):
    form = DoctorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save(commit=False)
        doctor.created_by = request.user
        doctor.save()
        messages.success(request, f"Dr. {doctor.name} was added to the directory.")
        return redirect("portal:doctors")
    return render(
        request,
        "portal/form_page.html",
        {
            "form": form,
            "title": "Add a doctor",
            "description": "Add a clinician to the shared directory.",
            "cancel_url": "portal:doctors",
            "submit_label": "Save doctor",
        },
    )


@login_required
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, created_by=request.user)
    form = DoctorForm(request.POST or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Dr. {doctor.name}'s profile was updated.")
        return redirect("portal:doctors")
    return render(
        request,
        "portal/form_page.html",
        {
            "form": form,
            "title": "Edit doctor",
            "description": f"Update Dr. {doctor.name}'s directory profile.",
            "cancel_url": "portal:doctors",
            "submit_label": "Save changes",
        },
    )


@login_required
@require_POST
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, created_by=request.user)
    name = doctor.name
    doctor.delete()
    messages.success(request, f"Dr. {name}'s profile was removed.")
    return redirect("portal:doctors")


@login_required
def assignment_list(request):
    assignments = PatientDoctorMapping.objects.filter(
        patient__created_by=request.user
    ).select_related("patient", "doctor")
    return render(request, "portal/assignment_list.html", {"assignments": assignments})


@login_required
def assignment_create(request):
    form = MappingForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        assignment = form.save()
        messages.success(
            request,
            f"Dr. {assignment.doctor.name} was assigned to {assignment.patient.name}.",
        )
        return redirect("portal:assignments")
    return render(
        request,
        "portal/form_page.html",
        {
            "form": form,
            "title": "Assign a doctor",
            "description": "Connect one of your patients with a clinician.",
            "cancel_url": "portal:assignments",
            "submit_label": "Create assignment",
        },
    )


@login_required
@require_POST
def assignment_delete(request, pk):
    assignment = get_object_or_404(
        PatientDoctorMapping.objects.select_related("patient", "doctor"),
        pk=pk,
        patient__created_by=request.user,
    )
    assignment.delete()
    messages.success(request, "The doctor assignment was removed.")
    return redirect("portal:assignments")
