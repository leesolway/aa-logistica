from django.db import models
from solo.models import SingletonModel

from allianceauth.authentication.models import State
from corptools.models import MapSystem


class LogisticaConfiguration(SingletonModel):
    """Global configuration for Logistica module"""

    aa_state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only contracts belonging to corporations in this state will be shown.",
    )

    class Meta:
        permissions = [
            ("view_logistica", "Can view logistics module"),
        ]

    def __str__(self):
        return "Logistica Configuration"


class ContractThreshold(models.Model):
    """Minimum stock threshold for a named contract type."""

    MATCH_EXACT = "exact"
    MATCH_CONTAINS = "contains"
    MATCH_CHOICES = [
        (MATCH_EXACT, "Exact match"),
        (MATCH_CONTAINS, "Contains"),
    ]

    solar_system = models.ForeignKey(
        MapSystem,
        on_delete=models.CASCADE,
        help_text="Solar system the contract must originate from.",
    )
    title = models.CharField(
        max_length=255,
        help_text="Contract title to match against.",
    )
    match_type = models.CharField(
        max_length=10,
        choices=MATCH_CHOICES,
        default=MATCH_EXACT,
        help_text="How to compare the title against contract names.",
    )
    minimum_count = models.PositiveIntegerField(
        help_text="Minimum number of outstanding contracts expected.",
    )

    class Meta:
        permissions = [
            ("manage_contract_thresholds", "Can manage contract thresholds"),
        ]
        ordering = ["solar_system__name", "title"]

    def __str__(self):
        return f"{self.solar_system.name} — {self.title} (min: {self.minimum_count})"

    def matches_title(self, contract_title: str) -> bool:
        if self.match_type == self.MATCH_CONTAINS:
            return self.title.lower() in (contract_title or "").lower()
        return self.title == (contract_title or "")
