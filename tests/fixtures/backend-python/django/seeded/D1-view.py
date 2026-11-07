from django.http import HttpResponse


def order_list(request) -> HttpResponse:
    return HttpResponse("orders")
