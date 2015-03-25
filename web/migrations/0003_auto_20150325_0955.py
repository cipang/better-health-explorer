# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20150318_0849'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articlesimilarity',
            options={'verbose_name_plural': 'ArticleSimilarity', 'verbose_name': 'ArticleSimilarity'},
        ),
        migrations.AddField(
            model_name='articleattr',
            name='care',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='articleattr',
            name='reading',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
