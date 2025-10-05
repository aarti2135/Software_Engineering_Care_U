import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexityValidator:
    """
    Requires at least one uppercase letter, one digit, and one special character.
    (MinimumLengthValidator handles length ≥ 8)
    """
    uppercase_re = re.compile(r'[A-Z]')
    digit_re = re.compile(r'\d')
    special_re = re.compile(r'[^A-Za-z0-9]')

    def validate(self, password, user=None):
        if not self.uppercase_re.search(password):
            raise ValidationError(_("Password must contain at least one uppercase letter."), code="password_no_upper")
        if not self.digit_re.search(password):
            raise ValidationError(_("Password must contain at least one digit."), code="password_no_digit")
        if not self.special_re.search(password):
            raise ValidationError(_("Password must contain at least one special character."), code="password_no_special")

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter, one digit, and one special character.")
