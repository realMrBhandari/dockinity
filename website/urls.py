from django.urls import path
from . import views

urlpatterns = [
    # core site urls
    path("", views.dockinity_home, name="dockinity-home"),
    path("new-docking-experiment", views.new_experiment, name="new-experiment"),
    path("docking-results", views.search_docking_result, name="search-result"),
    path(
        "docking-results/<str:experiment_id>",
        views.fetch_results_url,
        name="search-result-slug",
    ),
    path(
        "docking-results/",
        views.fetch_results_query,
        name="search-result-query",
    ),
    # utility based urls
    path(
        "request/receptor-config",
        views.receptor_components_input,
        name="get-receptor-config",
    ),
    path(
        "request/ligand-info",
        views.input_ligand_preview,
        name="get-ligand-preview",
    ),
    path(
        "request/csv-export",
        views.export_as_csv,
        name="export-result-csv",
    ),
]
