from django.db import models
import requests
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator,
    MinLengthValidator,
    MaxValueValidator,
)

# TODO: 1. prevent users from entering same ligand ids
# TODO: 2. add email auth
# TODO: 3. add email restrictions


# ! MODEL VALIDATORS
def validate_pdb_input(pdb_id):
    if not pdb_id.isalnum():
        raise ValidationError("PDB ID must be alphanumeric.")


def check_pdb_exists(pdb_id):
    response = requests.get(
        f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.upper()}",
        timeout=5,
    )
    if response.status_code != 200:
        raise ValidationError(f"PDB entry '{pdb_id}' does not exist.")


# ! MODEL OPTIONS

REQUEST_STATUS = [
    ("QUEUED", "QUEUED"),
    ("RUNNING", "RUNNING"),
    ("COMPLETED", "COMPLETED"),
    ("FAILED", "FAILED"),
]

DOCKING_TYPES = [("BLIND", "Blind Docking"), ("SITE_SPECIFIC", "Site Specific Docking")]

LIGAND_STATUS = [("DOCKED", "DOCKED"), ("FAILED", "FAILED")]

# ! CORE ORM SCHEMA


class ExperimentMetadata(models.Model):
    # ? for important info
    experiment_id = models.CharField(
        max_length=28,
        primary_key=True,
    )
    user_email = models.EmailField(
        max_length=250,
    )
    experiment_description = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    experiment_status = models.CharField(
        max_length=9, choices=REQUEST_STATUS, default="QUEUED"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    docked_structures_url = models.URLField(max_length=500, blank=True, null=True)


class ReceptorMolecule(models.Model):
    receptor_entry_id = models.BigAutoField(primary_key=True)
    provided_receptor = models.CharField(
        max_length=4,
        validators=[MinLengthValidator(4), validate_pdb_input, check_pdb_exists],
    )
    experiment_ref = models.OneToOneField(ExperimentMetadata, on_delete=models.PROTECT)

    receptor_structure_components = models.JSONField(
        default=dict,
    )
    selected_receptor_components = models.JSONField(
        default=dict,
    )


class LigandMolecules(models.Model):
    # ? for ligands
    ligand_entry_id = models.BigAutoField(primary_key=True)
    experiment_ref = models.ForeignKey(ExperimentMetadata, on_delete=models.PROTECT)
    provided_ligand = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    docking_status = models.CharField(max_length=6, choices=LIGAND_STATUS, blank=True)


class DockingParameters(models.Model):
    # ? for configuring autodock vina settings
    docking_parameters_entry_id = models.BigAutoField(primary_key=True)
    experiment_ref = models.OneToOneField(ExperimentMetadata, on_delete=models.PROTECT)
    docking_type = models.CharField(
        max_length=13, choices=DOCKING_TYPES, default="BLIND"
    )
    box_center_x = models.DecimalField(
        max_digits=7, decimal_places=5, blank=True, null=True
    )
    box_center_y = models.DecimalField(
        max_digits=7, decimal_places=5, blank=True, null=True
    )
    box_center_z = models.DecimalField(
        max_digits=7, decimal_places=5, blank=True, null=True
    )
    box_size_x = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    box_size_y = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    box_size_z = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )


class DockingResults(models.Model):
    # ? This is for result of every ligand
    result_record_id = models.BigAutoField(primary_key=True)
    experiment_ref = models.ForeignKey(ExperimentMetadata, on_delete=models.PROTECT)
    ligand_ref = models.ForeignKey(LigandMolecules, on_delete=models.PROTECT)
    pose_num = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    binding_affinity = models.DecimalField(max_digits=5, decimal_places=2)
    rmsd_lb = models.DecimalField(max_digits=7, decimal_places=5)
    rmsd_ub = models.DecimalField(max_digits=7, decimal_places=5)
