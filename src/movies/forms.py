from django import forms

from .models import Group, User


class SetNicknameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nickname"]

    def __init__(self, *args, **kwargs):
        super(SetNicknameForm, self).__init__(*args, **kwargs)
        self.fields["nickname"].widget.attrs.update(
            {
                "class": "form-control bg-dark text-light",
            }
        )


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
