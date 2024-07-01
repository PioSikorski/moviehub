from functools import wraps

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Group, User


class RequireNicknameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.COOKIES.get("nickname") and request.path != reverse(
            "set_nickname"
        ):
            return redirect("set_nickname")
        response = self.get_response(request)
        return response


def group_member_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        slug = kwargs.get("slug")
        if slug:
            nickname = request.COOKIES.get("nickname")
            user = get_object_or_404(User, nickname=nickname)
            group = get_object_or_404(Group, slug=slug)
            if user in group.members.all():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You are not authorized to view this group.")
                return redirect("index")
        else:
            messages.error(request, "Group slug is missing.")
            return redirect("index")

    return wrapper
