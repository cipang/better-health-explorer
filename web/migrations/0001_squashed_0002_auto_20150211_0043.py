# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [('web', '0001_initial'), ('web', '0002_auto_20150211_0043')]

    dependencies = [
        ('extract', '0003_auto_20150203_1852'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleAttr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('similarity', models.SmallIntegerField(default=0)),
                ('length', models.SmallIntegerField(default=0)),
                ('media', models.SmallIntegerField(default=0)),
                ('is_video', models.BooleanField(default=False)),
                ('is_local', models.BooleanField(default=False)),
                ('article', models.OneToOneField(to='extract.Article')),
            ],
            options={
                'verbose_name_plural': 'ArticleAttrs',
                'verbose_name': 'ArticleAttr',
            },
            bases=(models.Model,),
        ),
    ]
