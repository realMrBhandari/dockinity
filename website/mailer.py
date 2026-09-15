from django.core.mail import send_mail
from django.conf import settings


def notify_user_queued(experiment):
    message = f"""Greetings,

Your molecular docking experiment has been successfully submitted and is queued for processing. Your Experiment ID is  {experiment.experiment_id}

You can track your experiment's progress using the following link:
https://dockinity.com/docking-results/{experiment.experiment_id}

Regards,
Dockinity

"""

    send_mail(
        subject="Experiment received",
        message=message,
        from_email=f"Dockinity <{settings.DEFAULT_FROM_EMAIL}>",
        recipient_list=[experiment.user_email],
        fail_silently=False,
    )
