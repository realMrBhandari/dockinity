from django.core.exceptions import ValidationError


# ! Form Input Validators
def validate_ligands(input_data):
    if 1 <= len(input_data) <= 5 and all(item.isnumeric() for item in input_data):
        return True
    else:
        return False


def validate_chains(input_chains):
    if 1 <= len(input_chains):
        return True
    else:
        return False
