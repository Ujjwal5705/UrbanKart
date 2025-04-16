# Generated by Django 5.1.6 on 2025-04-16 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_alter_payment_created_at"),
        ("store", "0005_alter_variation_variation_category"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderproduct",
            name="color",
        ),
        migrations.RemoveField(
            model_name="orderproduct",
            name="size",
        ),
        migrations.RemoveField(
            model_name="orderproduct",
            name="variation",
        ),
        migrations.AddField(
            model_name="orderproduct",
            name="variations",
            field=models.ManyToManyField(blank=True, to="store.variation"),
        ),
    ]
