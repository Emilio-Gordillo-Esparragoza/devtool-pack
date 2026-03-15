from devpack.doctor.validator import validate_all


def doctor():
    """Check installation and PATH status."""
    validate_all()
