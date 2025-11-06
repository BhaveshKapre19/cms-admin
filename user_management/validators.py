import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class PasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))

        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least one uppercase letter."))

        if not re.search(r'[a-z]', password):
            raise ValidationError(_("Password must contain at least one lowercase letter."))

        if not re.search(r'[0-9]', password):
            raise ValidationError(_("Password must contain at least one digit."))

        if not re.search(r'[@$!%*?&#^()_+\-=\[\]{};:\'",.<>\/\\|`~]', password):
            raise ValidationError(_("Password must contain at least one special character."))

        if user:
            first_name = getattr(user, 'first_name', '') or ''
            last_name = getattr(user, 'last_name', '') or ''
            email = getattr(user, 'email', '') or ''

            # Make sure password doesn't contain personal info
            for value in [first_name, last_name, email.split('@')[0]]:
                if value and value.lower() in password.lower():
                    raise ValidationError(_("Password cannot contain your name or email."))

    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, including uppercase, lowercase, "
            "numbers, and special characters. It must not include your name or email."
        )
