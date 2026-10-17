from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient

User = get_user_model()


class StyledForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class PortalAuthenticationForm(StyledForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "The email or password you entered is incorrect.",
        "inactive": "This account is inactive.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["autofocus"] = True

    def clean(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        password = self.cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"])
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["inactive"])
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class RegistrationForm(StyledForm):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirmation = cleaned_data.get("password2")
        if password and confirmation and password != confirmation:
            self.add_error("password2", "The passwords do not match.")
        if password:
            candidate = User(
                username=cleaned_data.get("email", ""),
                email=cleaned_data.get("email", ""),
                first_name=cleaned_data.get("name", ""),
            )
            try:
                validate_password(password, user=candidate)
            except ValidationError as error:
                self.add_error("password1", error)
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["name"],
            password=self.cleaned_data["password1"],
        )


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)


class PatientForm(StyledModelForm):
    class Meta:
        model = Patient
        fields = (
            "name",
            "age",
            "gender",
            "phone",
            "address",
            "medical_history",
        )

    def clean_age(self):
        age = self.cleaned_data["age"]
        if age > 150:
            raise forms.ValidationError("Please enter a realistic age.")
        return age


class DoctorForm(StyledModelForm):
    class Meta:
        model = Doctor
        fields = ("name", "specialization", "email", "phone", "experience_years")


class MappingForm(StyledModelForm):
    class Meta:
        model = PatientDoctorMapping
        fields = ("patient", "doctor")

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.filter(created_by=user)
        self.fields["doctor"].queryset = Doctor.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        doctor = cleaned_data.get("doctor")
        if patient and doctor and PatientDoctorMapping.objects.filter(
            patient=patient, doctor=doctor
        ).exists():
            raise forms.ValidationError(
                "This doctor is already assigned to this patient."
            )
        return cleaned_data
