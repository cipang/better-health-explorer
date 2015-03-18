# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extract', '0003_auto_20150203_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='last_modified',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='remarks',
            field=models.CharField(max_length=150, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.URLField(blank=True, default=None, null=True),
            preserve_default=True,
        ),
    ]
