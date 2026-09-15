# DJANGO BUILT-IN MODULE IMPORTS
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils import timezone

# LOCAL MODULE IMPORTS
from . import mailer
from . import models
from .forms import ExperimentMetadataForm, DockingParametersForm, ReceptorMoleculeForm
from .services import orm_query_resuls, get_receptor_components, get_ligand_data
from .validators import validate_ligands, validate_chains

# PYTHON BUILT-IN MODULE IMPORTS
import csv
from io import StringIO
import re
import secrets

# Create your views here.


#  view responsible for rendering landing page || url dockinity.com
def dockinity_home(request):
    return render(request, "pages/home.html", {"active_page": "home"})


# view responsible for creating a new molecular docking experiment || url dockinity.com/new-docking-experiment
def new_experiment(request):
    # # Django model fields
    form_experiment_data = ExperimentMetadataForm()
    form_receptor_data = ReceptorMoleculeForm()
    form_docking_config = DockingParametersForm()

    if request.method == "POST":
        # # Model form bounding
        form_experiment_data = ExperimentMetadataForm(request.POST)
        form_receptor_data = ReceptorMoleculeForm(request.POST)
        form_docking_config = DockingParametersForm(request.POST)

        # # custom html form bounding
        submitted_ligands = request.POST.getlist("ligand_cid")
        selected_chains = request.POST.getlist("protein_component_chains")
        selected_ligands = request.POST.getlist("protein_component_ligands")
        selected_cofactors = request.POST.getlist("protein_component_cofactor")
        selected_mions = request.POST.getlist("protein_component_metal_ions")
        selected_hetatms = request.POST.getlist("protein_component_hetatm")

        if (
            form_experiment_data.is_valid()
            and form_receptor_data.is_valid()
            and form_docking_config.is_valid()
            and validate_ligands(submitted_ligands)
            and validate_chains(selected_chains)
        ):
            cleaned_experiment_data = form_experiment_data.cleaned_data
            cleaned_receptor_data = form_receptor_data.cleaned_data
            cleaned_docking_config = form_docking_config.cleaned_data

            # # --------- Constructing a dictionary from user's choices of Configure Receptor Components. This step includes grouping of the values based on component type. --------
            receptor_components = {}
            receptor_components.update({"chains": selected_chains})
            if len(selected_ligands) >= 1:
                receptor_components.update({"ligands": selected_ligands})
            if len(selected_cofactors) >= 1:
                receptor_components.update({"cofactors": selected_cofactors})
            if len(selected_mions) >= 1:
                receptor_components.update({"metal_ions": selected_mions})
            if len(selected_hetatms) >= 1:
                receptor_components.update({"other_hetero": selected_hetatms})

            receptor_structure = request.session.get("receptor_structure")

            generate_experiment_id = (
                f"DKN-{timezone.now():%Y-%m}-{secrets.token_urlsafe(12)}"
            )

            # # ----------- DJANGO ORM WRITE TO DATABASE -----------
            with transaction.atomic():
                exp_data = models.ExperimentMetadata.objects.create(
                    experiment_id=generate_experiment_id,
                    user_email=cleaned_experiment_data.get("user_email").strip(),
                    experiment_description=cleaned_experiment_data.get(
                        "experiment_description"
                    ),
                )

                receptor_data = models.ReceptorMolecule.objects.create(
                    provided_receptor=cleaned_receptor_data.get(
                        "provided_receptor"
                    ).upper(),
                    experiment_ref=exp_data,
                    receptor_structure_components=receptor_structure,
                    selected_receptor_components=receptor_components,
                )

                for lig in submitted_ligands:
                    models.LigandMolecules.objects.create(
                        experiment_ref=exp_data,
                        provided_ligand=int(lig),
                    )

                if cleaned_docking_config.get("docking_type") == "BLIND":
                    docking_parameters_data = models.DockingParameters.objects.create(
                        experiment_ref=exp_data,
                        docking_type=cleaned_docking_config.get("docking_type"),
                    )

                elif cleaned_docking_config.get("docking_type") == "SITE_SPECIFIC":
                    docking_parameters_data = models.DockingParameters.objects.create(
                        experiment_ref=exp_data,
                        docking_type=cleaned_docking_config.get("docking_type"),
                        box_center_x=cleaned_docking_config.get("box_center_x"),
                        box_center_y=cleaned_docking_config.get("box_center_y"),
                        box_center_z=cleaned_docking_config.get("box_center_z"),
                        box_size_x=cleaned_docking_config.get("box_size_x"),
                        box_size_y=cleaned_docking_config.get("box_size_y"),
                        box_size_z=cleaned_docking_config.get("box_size_z"),
                    )
            # # flushing session data
            request.session.flush()

            # # Email user sucess message
            mailer.notify_user_queued(experiment=exp_data)
            return redirect(
                "search-result-slug",
                experiment_id=exp_data.experiment_id,
            )

        else:
            return render(
                request,
                "pages/new-experiment.html",
                {
                    "form_experiment_data": form_experiment_data,
                    "form_receptor_data": form_receptor_data,
                    "form_docking_config": form_docking_config,
                    "active_page": "docking",
                },
            )

    return render(
        request,
        "pages/new-experiment.html",
        {
            "form_experiment_data": form_experiment_data,
            "form_receptor_data": form_receptor_data,
            "form_docking_config": form_docking_config,
            "active_page": "docking",
        },
    )


# view for results search page || url dockinity.com/docking-results
def search_docking_result(request):
    return render(
        request, "pages/search-experiment-results.html", {"active_page": "results"}
    )


# view for fetching result through direct url slug i.e. dockinity.com/docking-results/<experiment_id> | mostly for emails and stuff
def fetch_results_url(request, experiment_id):
    if re.fullmatch(r"^DKN-\d{4}-\d{2}-[A-Za-z0-9_-]{16}$", experiment_id):
        context = orm_query_resuls(experiment_id)
        return render(
            request,
            context.pop("html-template"),
            context,
        )
    else:
        raise Http404


# view for fetching result through search pages and search bars using view search_docking_result via url dockinity.com/docking-results/<experiment_id> | mostly for on site query
def fetch_results_query(request):
    experiment_id = request.GET.get("experiment_id").strip()
    context = orm_query_resuls(experiment_id)
    return render(
        request,
        context.pop("html-template"),
        context,
    )


# ! ================================ UTILITY VIEWS ==================================


# exports experiment result i.e. poses | affinity scores | rmsd values as csv file
def export_as_csv(request):
    experiment_id = request.POST.get("experiment_id", "").strip()
    if not re.fullmatch(
        r"^DKN-\d{4}-\d{2}-[A-Za-z0-9_-]{16}$",
        experiment_id,
    ):
        return HttpResponse(status=404)

    if not hasattr(export_as_csv, "csv_cache"):
        export_as_csv.csv_cache = {}

    if experiment_id in export_as_csv.csv_cache:
        csv_data = export_as_csv.csv_cache[experiment_id]

    else:
        try:
            experiment = (
                models.ExperimentMetadata.objects.select_related("receptormolecule")
                .prefetch_related(
                    Prefetch(
                        "ligandmolecules_set",
                        queryset=models.LigandMolecules.objects.prefetch_related(
                            "dockingresults_set"
                        ),
                    )
                )
                .get(
                    experiment_id=experiment_id,
                    experiment_status="COMPLETED",
                )
            )

        except models.ExperimentMetadata.DoesNotExist:
            return HttpResponse(status=404)

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "ligand",
                "receptor",
                "pose",
                "affinity",
                "rmsd_lb",
                "rmsd_ub",
            ]
        )

        receptor = experiment.receptormolecule.provided_receptor

        for ligand in experiment.ligandmolecules_set.all():
            if ligand.docking_status != "DOCKED":
                continue

            for result in ligand.dockingresults_set.all():
                writer.writerow(
                    [
                        ligand.provided_ligand,
                        receptor,
                        result.pose_num,
                        result.binding_affinity,
                        result.rmsd_lb,
                        result.rmsd_ub,
                    ]
                )

        csv_data = output.getvalue()

        export_as_csv.csv_cache[experiment_id] = csv_data

    response = HttpResponse(
        csv_data,
        content_type="text/csv",
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{experiment_id}-affinity-scores.csv"'
    )

    return response


# htmx view responsible for live rendering ligand card based on user input on new-experiment form
def input_ligand_preview(request):
    ligand_cid = request.POST.get("ligand_cid")
    print("Recieved HTMX Request for Ligand")
    ligand_cid = int(ligand_cid)
    fetched_ligand_info = get_ligand_data(ligand_cid)

    if fetched_ligand_info.get("status") == "success":

        molecule = fetched_ligand_info.get("data", {})
        ligand_input_number = int(request.POST.get("lig_input_number"))

        context = {
            "ligand_name": molecule.get("name", {}),
            "ligand_cid": ligand_cid,
            "ligand_weight": molecule.get("molecular_weight", {}),
            "ligand_logp": molecule.get("xlogp3_aa", {}),
            "ligand_hdb": molecule.get("hydrogen_bond_donor", {}),
            "ligand_hba": molecule.get("hydrogen_bond_acceptor", {}),
            "ligand_card_id": ligand_input_number,
        }

        return render(request, "fragments/ligand-preview-card.html", context)
    return HttpResponse("")


# htmx view fetches receptor component's from rcsb pdb and render's the input for selecting receptor components for docking
def receptor_components_input(request):
    pdb_input = request.POST.get("provided_receptor")
    print("Recieved HTMX Request for Protein")

    pdb_response = get_receptor_components(pdb_input)

    if pdb_response.get("status") == "success":
        pdb_response_data = pdb_response.get("data")
        print(f" THIS IS THE DATA I RECIEVED: \n {pdb_response_data} ")
        pdb_response_id = pdb_response_data.get("pdb_id")
        request.session["receptor_structure"] = pdb_response_data

        context = {"pdb_id": pdb_response_id, "pdb_structure": pdb_response_data}
        return render(request, "fragments/protein-component-input.html", context)

    return HttpResponse("")
