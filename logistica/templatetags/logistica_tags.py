from django import template

from allianceauth.authentication.models import CharacterOwnership

register = template.Library()

EVE_IMAGE_BASE = "https://images.evetech.net"


@register.simple_tag
def eve_image(category, entity_id, size=32):
    """Return an EVE image URL.

    Usage:
        {% eve_image "character" character_id 128 %}
        {% eve_image "corporation" corporation_id %}
        {% eve_image "alliance" alliance_id 64 %}
    """
    if category == "character":
        return f"{EVE_IMAGE_BASE}/characters/{entity_id}/portrait?size={size}"
    elif category == "corporation":
        return f"{EVE_IMAGE_BASE}/corporations/{entity_id}/logo?size={size}"
    elif category == "alliance":
        return f"{EVE_IMAGE_BASE}/alliances/{entity_id}/logo?size={size}"
    return ""


@register.simple_tag
def main_character(char_id):
    """Return the main character dict for an EVE character ID.

    Usage:
        {% main_character c.issuer_id as main %}

    Returns a dict with 'main_id' and 'main_name', or None.
    """
    if not char_id:
        return None
    try:
        ownership = CharacterOwnership.objects.select_related(
            "user__profile__main_character"
        ).get(character__character_id=char_id)
        main = ownership.user.profile.main_character
        if main:
            return {"main_id": main.character_id, "main_name": main.character_name}
    except CharacterOwnership.DoesNotExist:
        pass
    return None
