from django import forms
from django.urls import reverse
from .models import ExperimentMetadata, ReceptorMolecule, DockingParameters


class ExperimentMetadataForm(forms.ModelForm):
    class Meta:
        model = ExperimentMetadata
        fields = [
            "user_email",
            "experiment_description",
        ]

        widgets = {
            "user_email": forms.EmailInput(
                attrs={
                    "placeholder": "user@institute.edu",
                    "class": "req-form__input req-form__input-email",
                    "autocomplete": "email",
                    "required": "required",
                }
            ),
            "experiment_description": forms.Textarea(
                attrs={
                    "placeholder": "e.g. Evaluating small molecule's binding against SARS-CoV-2 main protease (6LU7)",
                    "class": "req-form__input req-form__input-description",
                    "autocomplete": "off",
                }
            ),
        }


class ReceptorMoleculeForm(forms.ModelForm):
    class Meta:
        model = ReceptorMolecule
        fields = ["provided_receptor"]
        widgets = {
            "provided_receptor": forms.TextInput(
                attrs={
                    "placeholder": "e.g. 6LU7",
                    "class": "req-form__input req-form__input-text",
                    "autocomplete": "off",
                    "id": "receptor-input-element",
                    "hx-post": "/request/receptor-config",
                    "hx-trigger": "input[this.value.length == 4] changed delay:150ms",
                    "hx-target": "#protein_panel",
                    "hx-swap": "innerHTML",
                    "required": "required",
                }
            ),
        }


class DockingParametersForm(forms.ModelForm):
    class Meta:
        model = DockingParameters
        exclude = ["experiment_ref", "pose_nums"]

        widgets = {
            "docking_type": forms.RadioSelect(
                attrs={
                    "class": "req-form__input req-form__input-radio",
                    "required": "required",
                }
            ),
            "box_center_x": forms.NumberInput(
                attrs={
                    "class": "req-form__input req-form__input-coordinate",
                    "autocomplete": "off",
                    "placeholder": "e.g. -10.807",
                    "required": "required",
                }
            ),
            "box_center_y": forms.NumberInput(
                attrs={
                    "class": "req-form__input req-form__input-coordinate",
                    "placeholder": "e.g. 12.541",
                    "autocomplete": "off",
                }
            ),
            "box_center_z": forms.NumberInput(
                attrs={
                    "class": "req-form__input req-form__input-coordinate",
                    "placeholder": "e.g. 68.917",
                    "autocomplete": "off",
                }
            ),
            "box_size_x": forms.NumberInput(
                attrs={
                    "class": "req-form__input req-form__input-coordinate",
                    "placeholder": "e.g. 30.0",
                    "autocomplete": "off",
                }
            ),
            "box_size_y": forms.NumberInput(
                attrs={
                    "class": "req-form__input req-form__input-coordinate",
                    "placeholder": "e.g. 30.0",
                    "autocomplete": "off",
                }
            ),
            "box_size_z": forms.NumberInput(
                attrs={
                    "class": "req-form__input req-form__input-coordinate",
                    "placeholder": "e.g. 30.0",
                    "autocomplete": "off",
                }
            ),
        }
