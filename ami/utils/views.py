from django.http import HttpResponse


def ping(request):
    html = '<html lang="en"><body>Hello AMI</body></html>'
    return HttpResponse(html)
