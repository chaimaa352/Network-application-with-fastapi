from datetime import datetime
from typing import Optional

from babel import Locale
from babel.dates import format_datetime

# Messages traduits
TRANSLATIONS = {
    "en": {
        "user_created": "User created successfully",
        "user_updated": "User updated successfully",
        "user_deleted": "User deleted successfully",
        "post_created": "Post created successfully",
        "post_updated": "Post updated successfully",
        "post_deleted": "Post deleted successfully",
        "comment_created": "Comment created successfully",
        "comment_deleted": "Comment deleted successfully",
        "not_found": "Resource not found",
        "invalid_params": "Invalid parameters",
        "invalid_body": "Invalid request body",
    },
    "fr": {
        "user_created": "Utilisateur créé avec succès",
        "user_updated": "Utilisateur mis à jour avec succès",
        "user_deleted": "Utilisateur supprimé avec succès",
        "post_created": "Publication créée avec succès",
        "post_updated": "Publication mise à jour avec succès",
        "post_deleted": "Publication supprimée avec succès",
        "comment_created": "Commentaire créé avec succès",
        "comment_deleted": "Commentaire supprimé avec succès",
        "not_found": "Ressource non trouvée",
        "invalid_params": "Paramètres invalides",
        "invalid_body": "Corps de requête invalide",
    },
}


class I18n:
    def __init__(self):
        self.locales = {"en": Locale("en", "US"), "fr": Locale("fr", "FR")}

    def format_date(self, date: datetime, language: str = "en") -> str:
        """Format date according to language with MM (01, 02, etc.)"""
        if not date:
            return ""

        lang = language.lower()[:2]
        if lang not in self.locales:
            lang = "en"

        locale = self.locales[lang]

        # Format avec MM (mois en nombres 01-12)
        if lang == "fr":
            # Format français : 15/01/2025 à 14:30
            return format_datetime(date, format="dd/MM/yyyy 'à' HH:mm", locale=locale)
        else:
            # Format anglais : 01/15/2025 at 2:30 PM
            return format_datetime(date, format="MM/dd/yyyy 'at' h:mm a", locale=locale)

    def get_translation(self, key: str, language: str = "en") -> str:
        """Get translation for a key"""
        lang = language.lower()[:2]
        if lang not in TRANSLATIONS:
            lang = "en"
        return TRANSLATIONS[lang].get(key, key)


_i18n = None


def setup_i18n():
    """Initialize i18n"""
    global _i18n
    _i18n = I18n()
    print(" i18n initialized")


def get_i18n() -> I18n:
    """Get i18n instance"""
    if _i18n is None:
        setup_i18n()
    return _i18n


def translate(key: str, language: str = "en") -> str:
    """Translate a key to the specified language"""
    return get_i18n().get_translation(key, language)


def format_date(date: Optional[datetime], language: str = "en") -> str:
    """Format a date according to the specified language"""
    if not date:
        return ""
    return get_i18n().format_date(date, language)
