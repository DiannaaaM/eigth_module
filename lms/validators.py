from urllib.parse import urlparse

from django.core.exceptions import ValidationError


ALLOWED_YOUTUBE_DOMAINS = {
    'youtube.com',
    'www.youtube.com',
    'm.youtube.com',
}


def validate_youtube_link(value: str) -> str:
    """Ensure that provided video link points to youtube.com."""
    if not value:
        return value

    parsed = urlparse(value)
    domain = parsed.netloc.lower()

    if domain not in ALLOWED_YOUTUBE_DOMAINS:
        raise ValidationError('Разрешены только ссылки на youtube.com.')

    return value
