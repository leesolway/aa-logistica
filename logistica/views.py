from collections import defaultdict

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from corptools.models import CorporateContract, MapSystem
from .models import ContractThreshold, LogisticaConfiguration


@login_required
@permission_required("logistica.view_logistica")
def index(request):
    """Main logistics dashboard"""
    config = LogisticaConfiguration.get_solo()

    if config.aa_state:
        chars = User.objects.filter(
            profile__state=config.aa_state
        ).values_list(
            "character_ownerships__character__character_id",
            "character_ownerships__character__corporation_id",
            "character_ownerships__character__alliance_id",
        )
        assignee_ids = set()
        for char_id, corp_id, alliance_id in chars:
            if char_id:
                assignee_ids.add(char_id)
            if corp_id:
                assignee_ids.add(corp_id)
            if alliance_id:
                assignee_ids.add(alliance_id)
    else:
        assignee_ids = set()

    base_qs = CorporateContract.objects.filter(
        contract_type="item_exchange",
        status="outstanding",
        assignee_id__in=assignee_ids,
    )

    rows = (
        base_qs.values(
            "title",
            "start_location_name__location_name",
            "start_location_name__system_id",
        )
        .annotate(count=Count("contract_id"))
        .order_by("start_location_name__location_name")
    )

    detail_qs = base_qs.select_related("issuer_name").values(
        "contract_id",
        "title",
        "issuer_id",
        "issuer_name__name",
        "price",
        "date_issued",
        "date_expired",
        "start_location_name__location_name",
    )

    detail_map = defaultdict(list)
    for c in detail_qs:
        loc = c["start_location_name__location_name"] or "Unknown Location"
        detail_map[(loc, c["title"] or "")].append(c)

    thresholds = list(ContractThreshold.objects.select_related("solar_system").all())

    def _threshold_for(system_id, title):
        for t in thresholds:
            if t.solar_system_id == system_id and t.matches_title(title):
                return t.minimum_count
        return None

    by_location = {}
    covered_thresholds = set()
    for row in rows:
        loc = row["start_location_name__location_name"] or "Unknown Location"
        system_id = row["start_location_name__system_id"]
        threshold = _threshold_for(system_id, row["title"] or "")
        row["threshold"] = threshold
        row["below_threshold"] = threshold is not None and row["count"] < threshold
        row["contracts"] = detail_map.get((loc, row["title"] or ""), [])
        by_location.setdefault(loc, []).append(row)
        for t in thresholds:
            if t.solar_system_id == system_id and t.matches_title(row["title"] or ""):
                covered_thresholds.add(t.pk)

    # Add zero-count rows for thresholds with no matching contracts
    for t in thresholds:
        if t.pk not in covered_thresholds:
            loc = t.solar_system.name
            by_location.setdefault(loc, []).append({
                "title": t.title,
                "count": 0,
                "threshold": t.minimum_count,
                "below_threshold": True,
                "contracts": [],
            })

    for rows_list in by_location.values():
        rows_list.sort(key=lambda r: (
            0 if (r["title"] or "").startswith("[") else 1,
            (r["title"] or "").lower()
        ))

    context = {
        "title": "Logistica",
        "by_location": by_location,
        "total": base_qs.count(),
    }
    return render(request, "logistica/index.html", context)


@login_required
@permission_required("logistica.manage_contract_thresholds")
def threshold_list(request):
    """List and manage contract thresholds."""
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            system_id = request.POST.get("solar_system")
            title = request.POST.get("title", "").strip()
            match_type = request.POST.get("match_type", ContractThreshold.MATCH_EXACT)
            minimum_count = request.POST.get("minimum_count")
            if system_id and title and minimum_count:
                system = get_object_or_404(MapSystem, pk=system_id)
                ContractThreshold.objects.create(
                    solar_system=system,
                    title=title,
                    match_type=match_type,
                    minimum_count=int(minimum_count),
                )
                messages.success(request, f"Threshold added for \"{title}\".")
            else:
                messages.error(request, "All fields are required.")

        elif action == "delete":
            threshold_id = request.POST.get("threshold_id")
            threshold = get_object_or_404(ContractThreshold, pk=threshold_id)
            threshold.delete()
            messages.success(request, f"Threshold \"{threshold.title}\" deleted.")

        return redirect("logistica:thresholds")

    thresholds = ContractThreshold.objects.select_related("solar_system").all()
    systems = MapSystem.objects.order_by("name")
    context = {
        "title": "Contract Thresholds",
        "thresholds": thresholds,
        "systems": systems,
        "match_choices": ContractThreshold.MATCH_CHOICES,
    }
    return render(request, "logistica/thresholds.html", context)
