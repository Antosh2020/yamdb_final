from datetime import datetime

from django.core.exceptions import ValidationError


def not_me_validator(value):
    """Check that authors name not me."""
    if value == "me":
        raise ValidationError(
            "Enter a valid username. This name is prohibited"
        )


def less_than_current(value):
    """
    Check that year of title is not less than 1900 and not more then current.
    """
    if value < 1900 or value > datetime.now().year:
        raise ValidationError(f'{value} is not valid year!')
