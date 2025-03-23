# Generated by Django 5.1.6 on 2025-03-22 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("carts", "0003_remove_cartitem_variations"),
        ("store", "0005_alter_variation_variation_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="variations",
            field=models.ManyToManyField(blank=True, to="store.variation"),
        ),
    ]
