from django.contrib import admin

from .models import Group, GroupMembership, GroupMovie, UserScore

admin.site.register(Group)
admin.site.register(GroupMembership)
admin.site.register(GroupMovie)
admin.site.register(UserScore)
