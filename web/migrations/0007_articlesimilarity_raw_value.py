# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_maintopic'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlesimilarity',
            name='raw_value',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
    ]
