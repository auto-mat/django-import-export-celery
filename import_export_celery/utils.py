import html2text
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse
from import_export.formats.base_formats import DEFAULT_FORMATS

DEFAULT_EXPORT_JOB_COMPLETION_MAIL_SUBJECT = "Django: Export job completed"
DEFAULT_EXPORT_JOB_COMPLETION_MAIL_TEMPLATE = (
    "email/export_job_completion.html"
)
IMPORT_EXPORT_CELERY_EXCLUDED_FORMATS = getattr(
    settings,
    "IMPORT_EXPORT_CELERY_EXCLUDED_FORMATS",
    [],
)


def get_formats():
    return [
        format
        for format in DEFAULT_FORMATS
        if format.TABLIB_MODULE.split(".")[-1].strip("_")
        not in IMPORT_EXPORT_CELERY_EXCLUDED_FORMATS
    ]


def build_html_and_text_message(template_name, context={}):
    """
    Render the given template with the context and returns
    the data in html and plain text format.
    """
    template = get_template(template_name)
    html_message = template.render(context)
    text_message = html2text.html2text(html_message)
    return html_message, text_message


def get_export_job_mail_context(export_job):
    context = {
        "app_label": export_job.app_label,
        "model": export_job.model,
        "link": export_job.site_of_origin
        + reverse(
            "admin:%s_%s_change"
            % (
                export_job._meta.app_label,
                export_job._meta.model_name,
            ),
            args=[export_job.pk],
        ),
    }
    return context


def get_export_job_mail_subject():
    return getattr(
        settings,
        "EXPORT_JOB_COMPLETION_MAIL_SUBJECT",
        DEFAULT_EXPORT_JOB_COMPLETION_MAIL_SUBJECT,
    )


def get_export_job_mail_template():
    return getattr(
        settings,
        "EXPORT_JOB_COMPLETION_MAIL_TEMPLATE",
        DEFAULT_EXPORT_JOB_COMPLETION_MAIL_TEMPLATE,
    )


def send_export_job_completion_mail(export_job):
    """
    Send export job completion mail
    """
    subject = get_export_job_mail_subject()
    template_name = get_export_job_mail_template()
    context = get_export_job_mail_context(export_job)
    context.update({"export_job": export_job})
    html_message, text_message = build_html_and_text_message(
        template_name, context
    )
    send_mail(
        subject=subject,
        message=text_message,
        html_message=html_message,
        from_email=settings.SERVER_EMAIL,
        recipient_list=[export_job.updated_by.email],
    )
