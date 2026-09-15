import requests
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from . import models


# ! function deals with querying database for results and experiment related data
def orm_query_resuls(experiment_id):
    try:
        experiment = (
            models.ExperimentMetadata.objects.select_related(
                "receptormolecule",
                "dockingparameters",
            )
            .prefetch_related(
                "ligandmolecules_set__dockingresults_set",
            )
            .get(experiment_id=experiment_id)
        )

    except models.ExperimentMetadata.DoesNotExist:

        data = {
            "status": "INVALID",
        }
        context = {
            "html-template": "pages/experiment-result-invalid.html",
            "experiment_id": experiment_id,
            "active_page": "results",
        }
        return context

    else:

        if experiment.experiment_status == "COMPLETED":

            data = {
                "experiment_id": experiment.experiment_id,
                "experiment_status": experiment.experiment_status,
                "experiment_description": experiment.experiment_description,
                "receptor": experiment.receptormolecule.provided_receptor,
                "receptor_components": {
                    "chains": experiment.receptormolecule.selected_receptor_components[
                        "chains"
                    ],
                },
                "ligands": {
                    str(ligand.provided_ligand): {
                        "id": ligand.ligand_entry_id,
                        "results": [
                            {
                                "pose": result.pose_num,
                                "affinity": float(result.binding_affinity),
                                "rmsd_lb": float(result.rmsd_lb),
                                "rmsd_ub": float(result.rmsd_ub),
                            }
                            for result in ligand.dockingresults_set.all()
                        ],
                        "docking_status": ligand.docking_status,
                    }
                    for ligand in experiment.ligandmolecules_set.all()
                },
                "docking_mode": experiment.dockingparameters.docking_type,
                "center_x": (
                    float(experiment.dockingparameters.box_center_x)
                    if experiment.dockingparameters.box_center_x is not None
                    else None
                ),
                "center_y": (
                    float(experiment.dockingparameters.box_center_y)
                    if experiment.dockingparameters.box_center_y is not None
                    else None
                ),
                "center_z": (
                    float(experiment.dockingparameters.box_center_z)
                    if experiment.dockingparameters.box_center_z is not None
                    else None
                ),
                "size_x": (
                    float(experiment.dockingparameters.box_size_x)
                    if experiment.dockingparameters.box_size_x is not None
                    else None
                ),
                "size_y": (
                    float(experiment.dockingparameters.box_size_y)
                    if experiment.dockingparameters.box_size_y is not None
                    else None
                ),
                "size_z": (
                    float(experiment.dockingparameters.box_size_z)
                    if experiment.dockingparameters.box_size_z is not None
                    else None
                ),
                "docked_structures_url": experiment.docked_structures_url,
                "completed_at": timezone.make_aware(
                    datetime.strptime(
                        experiment.completed_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        "%Y-%m-%d %H:%M:%S.%f",
                    ),
                    dt_timezone.utc,
                ),
                "duration": (
                    timezone.now().timestamp() - experiment.completed_at.timestamp()
                )
                / 86400,
            }

            ligand_result = dict(
                sorted(
                    data["ligands"].items(),
                    key=lambda item: (
                        item[1]["docking_status"] != "DOCKED",
                        (
                            item[1]["results"][0]["affinity"]
                            if item[1]["docking_status"] == "DOCKED"
                            else 0
                        ),
                    ),
                )
            )
            ligand_metadata = {
                "total_docked": len(
                    [
                        ligs
                        for ligs, vals in ligand_result.items()
                        if vals["docking_status"] == "DOCKED"
                    ]
                ),
                "total_ligands": len(ligand_result.keys()),
                "failed_ligands": len(
                    [
                        ligs
                        for ligs, vals in ligand_result.items()
                        if vals["docking_status"] == "FAILED"
                    ]
                ),
            }
            context = {
                "active_page": "results",
                "experiment_meta": data,
                "ligand_metadata": ligand_metadata,
                "ligand_result": ligand_result,
                "html-template": "pages/experiment-result-sucess.html",
            }

            return context

        elif experiment.experiment_status in ("QUEUED", "FAILED"):

            queued_data = {
                "experiment_id": experiment.experiment_id,
                "experiment_description": experiment.experiment_description,
                "created_at": timezone.make_aware(
                    datetime.strptime(
                        experiment.created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        "%Y-%m-%d %H:%M:%S.%f",
                    ),
                    dt_timezone.utc,
                ),
                "completed_at": (
                    timezone.make_aware(
                        datetime.strptime(
                            experiment.completed_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
                            "%Y-%m-%d %H:%M:%S.%f",
                        ),
                        dt_timezone.utc,
                    )
                    if experiment.completed_at is not None
                    else None
                ),
                "experiment_status": experiment.experiment_status,
                "receptor": experiment.receptormolecule.provided_receptor,
                "receptor_components": {
                    "chains": experiment.receptormolecule.selected_receptor_components[
                        "chains"
                    ],
                },
                "ligands": [
                    str(ligand.provided_ligand)
                    for ligand in experiment.ligandmolecules_set.all()
                ],
                "docking_mode": experiment.dockingparameters.docking_type,
                "center_x": (
                    float(experiment.dockingparameters.box_center_x)
                    if experiment.dockingparameters.box_center_x is not None
                    else None
                ),
                "center_y": (
                    float(experiment.dockingparameters.box_center_y)
                    if experiment.dockingparameters.box_center_y is not None
                    else None
                ),
                "center_z": (
                    float(experiment.dockingparameters.box_center_z)
                    if experiment.dockingparameters.box_center_z is not None
                    else None
                ),
                "size_x": (
                    float(experiment.dockingparameters.box_size_x)
                    if experiment.dockingparameters.box_size_x is not None
                    else None
                ),
                "size_y": (
                    float(experiment.dockingparameters.box_size_y)
                    if experiment.dockingparameters.box_size_y is not None
                    else None
                ),
                "size_z": (
                    float(experiment.dockingparameters.box_size_z)
                    if experiment.dockingparameters.box_size_z is not None
                    else None
                ),
            }
            context = {
                "fetched_data": queued_data,
                "total_ligands": len(queued_data.get("ligands")),
                "active_page": "results",
                "html-template": "pages/experiment-result-status.html",
            }
            return context


# ! PUBCHEM API
def get_ligand_data(molecular_id):
    property_url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
        f"cid/{molecular_id}/property/"
        f"MolecularWeight,XLogP,HBondDonorCount,HBondAcceptorCount/JSON"
    )

    synonym_url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
        f"cid/{molecular_id}/synonyms/JSON"
    )

    try:
        # ================= PROPERTY REQUEST =================

        property_response = requests.get(
            property_url,
            timeout=10,
        )

        print("PROPERTY STATUS:", property_response.status_code)

        if property_response.status_code in (400, 404):
            return {
                "status": "invalid_input",
                "data": None,
            }

        property_response.raise_for_status()

        # ================= SYNONYM REQUEST =================

        synonym_response = requests.get(
            synonym_url,
            timeout=10,
        )

        print("SYNONYM STATUS:", synonym_response.status_code)

        if synonym_response.status_code in (400, 404):
            return {
                "status": "invalid_input",
                "data": None,
            }

        synonym_response.raise_for_status()

        # ================= PARSE RESPONSE =================

        properties = property_response.json()["PropertyTable"]["Properties"][0]

        synonyms = synonym_response.json()["InformationList"]["Information"][0][
            "Synonym"
        ]

        # ================= RETURN DATA =================

        return {
            "status": "success",
            "data": {
                "name": synonyms[0],
                "molecular_weight": float(properties["MolecularWeight"]),
                "xlogp3_aa": properties["XLogP"],
                "hydrogen_bond_donor": properties["HBondDonorCount"],
                "hydrogen_bond_acceptor": properties["HBondAcceptorCount"],
            },
        }

    # ================= REQUEST ERRORS =================

    except requests.Timeout as e:

        print("========== PUBCHEM TIMEOUT ==========")
        print(repr(e))

        return {
            "status": "api_error",
            "data": None,
        }

    except requests.ConnectionError as e:

        print("========== PUBCHEM CONNECTION ERROR ==========")
        print(repr(e))

        return {
            "status": "api_error",
            "data": None,
        }

    except requests.RequestException as e:

        print("========== PUBCHEM REQUEST ERROR ==========")
        print(repr(e))

        return {
            "status": "api_error",
            "data": None,
        }

    # ================= RESPONSE DATA ERRORS =================

    except (KeyError, IndexError, TypeError, ValueError) as e:

        print("========== PUBCHEM DATA PARSING ERROR ==========")
        print(repr(e))

        return {
            "status": "invalid_data",
            "data": None,
        }


# ! PUBCHEM API FROM MOBILE

# def get_receptor_components(molecular_id):
#     print("recieved request")
#     synonym_url = (
#         f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
#         f"cid/{molecular_id}/synonyms/JSON"
#     )

#     try:
#         response = requests.get(synonym_url, timeout=10)

#         if response.status_code in (400, 404):
#             return {
#                 "status": "invalid_input",
#                 "data": None,
#             }

#         response.raise_for_status()

#         synonyms = response.json()["InformationList"]["Information"][0]["Synonym"]

#         return {
#             "status": "success",
#             "data": synonyms[0],
#         }

#     except requests.Timeout:
#         return {
#             "status": "api_error",
#             "data": None,
#         }

#     except requests.ConnectionError:
#         return {
#             "status": "api_error",
#             "data": None,
#         }

#     except requests.RequestException:
#         return {
#             "status": "api_error",
#             "data": None,
#         }

#     except (KeyError, IndexError, TypeError, ValueError):
#         return {
#             "status": "invalid_data",
#             "data": None,
#         }


# ! RCSB PDB API ===================================================================================================
# ? for protein tunning feedback
def get_receptor_components(pdb_id):

    RCSB_GRAPHQL = "https://data.rcsb.org/graphql"

    METAL_IONS = {
        "LI": "Li⁺",
        "NA": "Na⁺",
        "K": "K⁺",
        "RB": "Rb⁺",
        "CS": "Cs⁺",
        "MG": "Mg²⁺",
        "CA": "Ca²⁺",
        "SR": "Sr²⁺",
        "BA": "Ba²⁺",
        "MN": "Mn²⁺",
        "FE": "Fe",
        "CO": "Co²⁺",
        "NI": "Ni²⁺",
        "CU": "Cu²⁺",
        "ZN": "Zn²⁺",
        "CD": "Cd²⁺",
        "HG": "Hg²⁺",
        "CR": "Cr",
        "MO": "Mo",
        "W": "W",
    }

    COFACTORS = {
        "HEM",
        "NAD",
        "NAP",
        "FAD",
        "FMN",
        "SAM",
        "SAH",
        "ATP",
        "ADP",
        "GDP",
        "GTP",
        "PLP",
        "THF",
    }

    OTHER_HETERO = {
        "SO4",
        "PO4",
        "CO3",
        "NO3",
        "ACT",
        "ACE",
        "MES",
        "TRS",
        "HEP",
        "EPE",
        "CIT",
    }

    #! VALIDATE INPUT

    if not isinstance(pdb_id, str):
        return {
            "status": "invalid_input",
            "data": None,
            "message": "PDB ID must be a alphanumeric string.",
        }

    pdb_id = pdb_id.strip().upper()

    if not pdb_id:
        return {
            "status": "invalid_input",
            "data": None,
            "message": "PDB ID cannot be empty.",
        }

    if len(pdb_id) != 4:
        return {
            "status": "invalid_input",
            "data": None,
            "message": "PDB ID must contain exactly 4 characters.",
        }

    # GRAPHQL QUERY

    QUERY = """
    query StructureInventory($pdb_id: String!) {

        entry(entry_id: $pdb_id) {

            rcsb_id

            polymer_entities {

                rcsb_polymer_entity_container_identifiers {
                    entity_id
                    auth_asym_ids
                }

                entity_poly {
                    pdbx_seq_one_letter_code_can
                }
            }

            nonpolymer_entities {

                rcsb_nonpolymer_entity_container_identifiers {
                    entity_id
                    nonpolymer_comp_id
                }

                nonpolymer_comp {

                    chem_comp {
                        id
                        name
                        type
                        formula
                    }
                }
            }
        }
    }
    """

    # BUILD REQUEST

    payload = json.dumps(
        {
            "query": QUERY,
            "variables": {
                "pdb_id": pdb_id,
            },
        }
    ).encode("utf-8")

    request = Request(
        RCSB_GRAPHQL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Dockinity",
        },
        method="POST",
    )

    # SEND REQUEST

    try:

        with urlopen(request, timeout=15) as response:
            raw_response = response.read().decode("utf-8")

    except HTTPError as error:

        if error.code == 400:
            return {
                "status": "api_error",
                "data": None,
                "message": "RCSB rejected the request.",
            }

        if 500 <= error.code < 600:
            return {
                "status": "api_error",
                "data": None,
                "message": (
                    "RCSB is currently experiencing a server error. "
                    "Please try again later."
                ),
            }

        return {
            "status": "api_error",
            "data": None,
            "message": f"RCSB returned HTTP error {error.code}.",
        }

    except URLError:
        return {
            "status": "connection_error",
            "data": None,
            "message": (
                "Unable to connect to the RCSB API. "
                "Please check your internet connection."
            ),
        }

    except TimeoutError:
        return {
            "status": "timeout",
            "data": None,
            "message": ("The request to RCSB timed out. " "Please try again."),
        }

    # PARSE JSON RESPONSE

    try:

        data = json.loads(raw_response)

    except json.JSONDecodeError:
        return {
            "status": "api_error",
            "data": None,
            "message": "RCSB returned an invalid JSON response.",
        }

    # GRAPHQL ERRORS

    if data.get("errors"):

        errors = data["errors"]

        messages = []

        for error in errors:

            if isinstance(error, dict):

                message = error.get("message")

                if message:
                    messages.append(message)

        if messages:
            return {
                "status": "api_error",
                "data": None,
                "message": "; ".join(messages),
            }

        return {
            "status": "api_error",
            "data": None,
            "message": "RCSB returned a GraphQL error.",
        }

    # VALIDATE RESPONSE STRUCTURE

    response_data = data.get("data")

    if not isinstance(response_data, dict):
        return {
            "status": "api_error",
            "data": None,
            "message": "RCSB returned an unexpected response.",
        }

    # GET ENTRY

    entry = response_data.get("entry")

    if entry is None:
        return {
            "status": "not_found",
            "data": None,
            "message": f"PDB entry '{pdb_id}' was not found.",
        }

    # RESULT DICTIONARY

    result = {
        "pdb_id": pdb_id,
        "chains": {},
        "ligands": {},
        "cofactors": {},
        "metal_ions": {},
        "other_hetero": {},
    }

    # PROTEIN CHAINS

    for entity in entry.get("polymer_entities") or []:

        identifiers = entity.get(
            "rcsb_polymer_entity_container_identifiers",
            {},
        )

        chain_ids = identifiers.get("auth_asym_ids", [])

        entity_poly = entity.get("entity_poly") or {}

        sequence = entity_poly.get("pdbx_seq_one_letter_code_can") or ""

        residue_count = len(sequence.replace("\n", "").replace(" ", ""))

        for chain_id in chain_ids:

            result["chains"][chain_id] = f"Chain {chain_id} ({residue_count} residues)"

    # NON-POLYMER COMPONENTS

    for entity in entry.get("nonpolymer_entities") or []:

        identifiers = entity.get(
            "rcsb_nonpolymer_entity_container_identifiers",
            {},
        )

        component_id = identifiers.get("nonpolymer_comp_id")

        if not component_id:
            continue

        nonpolymer_comp = entity.get("nonpolymer_comp") or {}

        chem_comp = nonpolymer_comp.get("chem_comp") or {}

        name = chem_comp.get(
            "name",
            component_id,
        )

        # METAL ION

        if component_id in METAL_IONS:

            result["metal_ions"][component_id] = METAL_IONS[component_id]

            continue

        # COFACTOR

        if component_id in COFACTORS:

            result["cofactors"][component_id] = name

            continue

        # OTHER HETERO

        if component_id in OTHER_HETERO:

            result["other_hetero"][component_id] = name

            continue

        # LIGAND

        result["ligands"][component_id] = name

    # SUCCESS

    return {
        "status": "success",
        "data": result,
        "message": None,
    }
