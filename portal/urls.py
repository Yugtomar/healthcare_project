from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.PortalLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.PortalLogoutView.as_view(), name="logout"),
    path("patients/", views.patient_list, name="patients"),
    path("patients/new/", views.patient_create, name="patient-create"),
    path("patients/<int:pk>/edit/", views.patient_update, name="patient-update"),
    path("patients/<int:pk>/delete/", views.patient_delete, name="patient-delete"),
    path("doctors/", views.doctor_list, name="doctors"),
    path("doctors/new/", views.doctor_create, name="doctor-create"),
    path("doctors/<int:pk>/edit/", views.doctor_update, name="doctor-update"),
    path("doctors/<int:pk>/delete/", views.doctor_delete, name="doctor-delete"),
    path("assignments/", views.assignment_list, name="assignments"),
    path("assignments/new/", views.assignment_create, name="assignment-create"),
    path(
        "assignments/<int:pk>/delete/",
        views.assignment_delete,
        name="assignment-delete",
    ),
]
