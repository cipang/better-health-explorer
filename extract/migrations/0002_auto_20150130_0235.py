# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extract', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='last_modified',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='remarks',
            field=models.CharField(max_length=150, null=True),
            preserve_default=True,
        ),
    ]
