# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleattr',
            name='color',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
    ]
