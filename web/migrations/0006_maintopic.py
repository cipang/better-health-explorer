# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_articleattr_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Topic name')),
                ('article_id', models.IntegerField(verbose_name='Linked to article ID')),
            ],
            options={
                'verbose_name': 'Main Topic',
                'verbose_name_plural': 'Main Topics',
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
