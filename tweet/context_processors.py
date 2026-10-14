from django.conf import settings


def auth_features(request):
    return {
        'google_login_enabled': bool(
            getattr(settings, 'GOOGLE_CLIENT_ID', '')
            and getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        ),
    }

