# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_squashed_0002_auto_20150211_0043'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleSimilarity',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('a', models.IntegerField(verbose_name='Article A (with smaller ID)')),
                ('b', models.IntegerField(verbose_name='Article B (with bigger ID)')),
                ('similarity', models.SmallIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'ArticleSimilaritys',
                'verbose_name': 'ArticleSimilarity',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='articlesimilarity',
            unique_together=set([('a', 'b')]),
        ),
        migrations.RemoveField(
            model_name='articleattr',
            name='similarity',
        ),
    ]
