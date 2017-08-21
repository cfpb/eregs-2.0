from django.conf import settings


LEGACY_JSON_LOOKUPS = getattr(settings, 'LEGACY_JSON_LOOKUPS', False)
