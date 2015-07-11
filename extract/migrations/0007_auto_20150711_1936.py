# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extract', '0006_auto_20150709_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='name',
            field=models.CharField(verbose_name='Keyword', max_length=200, db_index=True),
            preserve_default=True,
        ),
    ]
