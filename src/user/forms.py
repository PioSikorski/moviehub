from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control bg-dark text-light",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control bg-dark text-light",
            }
        )
