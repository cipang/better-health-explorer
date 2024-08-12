# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extract', '0005_auto_20150427_2018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category3',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Category 3 Name')),
                ('article', models.ForeignKey(to='extract.Article', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name_plural': 'Category3',
                'verbose_name': 'Category3',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category35',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Category 35 Name')),
                ('article', models.ForeignKey(to='extract.Article', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name_plural': 'Category35',
                'verbose_name': 'Category35',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Keyword')),
                ('article', models.ForeignKey(to='extract.Article', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name_plural': 'Keywords',
                'verbose_name': 'Keyword',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='article',
            name='cat2',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='provider',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='unique_key',
            field=models.CharField(max_length=200, default=None, null=True, unique=True, blank=True),
            preserve_default=True,
        ),
    ]
