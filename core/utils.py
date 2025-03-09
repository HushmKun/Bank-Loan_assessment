from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator



PERCENTAGE_VALIDATOR = [MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))]
