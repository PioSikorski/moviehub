def user_groups(request):
    user = request.user
    if user.is_authenticated:
        groups = user.group_memberships.all()
    else:
        groups = None
    return {"groups": groups}
