from tortoise import fields
from tortoise.models import Model


class Rate(Model):
    cargo_type = fields.CharField(max_length=255)
    rate = fields.DecimalField(max_digits=5, decimal_places=3)
    valid_from = fields.DatetimeField(auto_now_add=True)


class InsuranceRequest(Model):
    cargo_type = fields.CharField(max_length=255)
    declared_value = fields.DecimalField(max_digits=10, decimal_places=2)
    timestamp = fields.DatetimeField(auto_now_add=True)
