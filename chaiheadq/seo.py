"""Small public SEO endpoints for the Chai & Chatter site."""

from django.http import HttpResponse
from django.views.decorators.http import require_GET


SITE_URL = "https://chai-chatter.ajeetrawat.me"
PUBLIC_PATHS = ("/", "/search/", "/chai/")


@require_GET
def sitemap(request):
    entries = "".join(
        f"  <url><loc>{SITE_URL}{path}</loc></url>\n"
        for path in PUBLIC_PATHS
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}"
        "</urlset>\n"
    )
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")


@require_GET
def robots(request):
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /accounts/\n"
        "Disallow: /admin/\n"
        "Disallow: /tweet/\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
