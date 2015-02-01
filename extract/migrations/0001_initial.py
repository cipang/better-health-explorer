# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('source', models.CharField(max_length=5)),
                ('url', models.URLField(null=True, default=None)),
                ('title', models.CharField(max_length=200)),
                ('summary', models.TextField()),
                ('content', models.TextField()),
                ('category', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('src', models.URLField()),
                ('alt', models.CharField(max_length=50)),
                ('article', models.ForeignKey(to='extract.Article')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
            bases=(models.Model,),
        ),
    ]
