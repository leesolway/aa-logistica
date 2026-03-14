from celery import shared_task
from esi.errors import TokenInvalidError
from esi.models import Token
from requests.exceptions import HTTPError

from allianceauth.services.hooks import get_extension_logger

from corptools import providers
from corptools.models import CorporateContract, EveLocation, MapSystem

logger = get_extension_logger(__name__)

REQ_SCOPE = 'esi-universe.read_structures.v1'
RESOLVE_BATCH_SIZE = 50


def _resolve_structure(location_id):
    """Try to resolve a structure location using any available token with the right scope.

    Returns the EveLocation on success, None if no token could access it,
    or raises HTTPError if ESI returned an error status.
    """
    tokens = Token.objects.filter(scopes__name=REQ_SCOPE)
    for token in tokens:
        try:
            structure = providers.esi.client.Universe.get_universe_structures_structure_id(
                structure_id=location_id,
                token=token.valid_access_token()
            ).result()
        except TokenInvalidError:
            continue
        except HTTPError:
            raise
        except Exception:
            continue

        system = MapSystem.objects.filter(system_id=structure.get('solar_system_id')).first()
        if system is None:
            continue

        loc, _ = EveLocation.objects.get_or_create(location_id=location_id)
        loc.location_name = structure.get('name')
        loc.system = system
        loc.save()
        return loc

    return None


@shared_task(name="logistica.tasks.resolve_contract_locations")
def resolve_contract_locations():
    """Resolve CorporateContract locations that are unresolved."""
    location_ids = list(
        (
            set(CorporateContract.objects.filter(
                start_location_name__isnull=True,
                start_location_id__isnull=False,
            ).values_list("start_location_id", flat=True))
            | set(CorporateContract.objects.filter(
                end_location_name__isnull=True,
                end_location_id__isnull=False,
            ).values_list("end_location_id", flat=True))
        )
    )[:RESOLVE_BATCH_SIZE]

    resolved = 0
    failed = 0
    skipped_ids = set()
    for location_id in location_ids:
        if location_id in skipped_ids:
            continue

        try:
            loc = _resolve_structure(location_id)
        except HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            logger.warning(
                f"Logistica: ESI returned HTTP {status} for structure {location_id} — skipping for this run"
            )
            skipped_ids.add(location_id)
            failed += 1
            continue

        if loc:
            CorporateContract.objects.filter(
                start_location_id=location_id, start_location_name__isnull=True
            ).update(start_location_name=loc)
            CorporateContract.objects.filter(
                end_location_id=location_id, end_location_name__isnull=True
            ).update(end_location_name=loc)
            resolved += 1
        else:
            logger.warning(
                f"Logistica: No token could resolve structure {location_id} — skipping for this run"
            )
            skipped_ids.add(location_id)
            failed += 1

    logger.info(f"Logistica: Resolved {resolved}, failed/skipped {failed} of {len(location_ids)} contract locations")
    return f"Resolved {resolved}, failed/skipped {failed}"
