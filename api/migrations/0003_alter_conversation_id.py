# Generated by Django 5.1.6 on 2025-02-15 12:32

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_customersupportrepprofile_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
