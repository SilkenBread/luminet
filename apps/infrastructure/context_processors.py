from django.conf import settings


def global_settings(request):
    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'GOOGLE_MAPS_MAP_ID': getattr(settings, 'GOOGLE_MAPS_MAP_ID', ''),
    }

    # Add areas for sidebar (only for authenticated users)
    if request.user.is_authenticated:
        from apps.users.models import Area
        context['sidebar_areas'] = Area.objects.filter(is_active=True).values_list('name', flat=True)

    return context
