from django.conf import settings
from django.core import signing
from django.core.management.base import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    help = "Create a signed admin registration invite link."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="",
            help="Optional email restriction for the invite.",
        )
        parser.add_argument(
            "--base-url",
            default="",
            help="Base URL for generated link, e.g. https://classmark.onrender.com",
        )

    def handle(self, *args, **options):
        email = (options["email"] or "").strip().lower()
        payload = {}
        if email:
            payload["email"] = email

        token = signing.dumps(payload, salt="users.admin_invite")
        path = reverse("users:admin_register", kwargs={"token": token})
        base_url = (options["base_url"] or getattr(settings, "SITE_BASE_URL", "")).strip().rstrip("/")

        self.stdout.write(self.style.SUCCESS("Admin invite token generated."))
        self.stdout.write(f"Token: {token}")
        self.stdout.write(f"Path: {path}")
        if base_url:
            self.stdout.write(f"URL: {base_url}{path}")
