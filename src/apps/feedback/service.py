from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from src.apps.feedback.constants import EMAIL_TEMPLATE
from src.apps.feedback.models import FeedbackRequest, EmailRecipient
from src.apps.users import User


def send_new_feedback_request_notify(fr: FeedbackRequest):
    send_mail(
        subject=f'Новая заявка от "{fr.requestener_name}", создана в {fr.created_at.strftime("%H:%M %d/%m/%y")}',
        message=render_to_string(EMAIL_TEMPLATE, {"request": fr}),
        from_email=f"noreply@{settings.MAIN_DOMAIN}",
        recipient_list=[recipient.email for recipient in EmailRecipient.objects.all()],
    )


def mark_feedback_request_as_served(fr: FeedbackRequest, manager: User):
    # TODO:
    # - set is_served = True
    # - set served_by = manager
    # - check here manages.is_stuff
    pass
