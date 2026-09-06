import re

from django.core.exceptions import ValidationError

REFERENCE_RE = re.compile(r"^[A-Z0-9_\-/]+$")
DIMENSION_RE = re.compile(r"^(\d{3})/(\d{2,3})\s*R(\d{2})\s*(\d{2,3})([A-Z])$", re.IGNORECASE)


def validate_reference(value):
    normalized = (value or "").upper()
    if not REFERENCE_RE.fullmatch(normalized):
        raise ValidationError("La référence accepte uniquement lettres, chiffres, tirets, underscores et barres obliques, sans espace.")


def validate_dimension(value):
    match = DIMENSION_RE.fullmatch((value or "").strip())
    if not match:
        raise ValidationError("Format attendu : 205/55 R16 91V.")
    width, height, diameter, load, _speed = match.groups()
    if not 125 <= int(width) <= 445:
        raise ValidationError("La largeur doit être comprise entre 125 et 445 mm.")
    if not 20 <= int(height) <= 100:
        raise ValidationError("La hauteur doit être comprise entre 20 et 100.")
    if not 10 <= int(diameter) <= 30:
        raise ValidationError("Le diamètre doit être compris entre 10 et 30 pouces.")
    if not 50 <= int(load) <= 200:
        raise ValidationError("Indice de charge non réaliste.")


def validate_image_size(image):
    if image and image.size > 5 * 1024 * 1024:
        raise ValidationError("L'image ne doit pas dépasser 5 Mo.")

