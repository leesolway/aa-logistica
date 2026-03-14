from allianceauth import hooks
from allianceauth.services.hooks import UrlHook, MenuItemHook
from django.utils.translation import gettext_lazy as _

from . import urls as logistica_urls


@hooks.register("url_hook")
def register_urls():
    return UrlHook(logistica_urls, "logistica", r"^logistica/")


class LogisticaMainMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(
            self,
            _("Logistica"),
            "fa-solid fa-truck",
            "logistica:index",
            navactive=["logistica:index"]
        )

    def render(self, request):
        if request.user.is_staff or request.user.has_perm("logistica.view_logistica"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_logistica_menu():
    return LogisticaMainMenu()
