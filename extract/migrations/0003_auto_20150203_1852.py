# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extract', '0002_auto_20150130_0235'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutLink',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('target_source', models.CharField(max_length=5)),
                ('target_url', models.URLField()),
                ('alt', models.CharField(max_length=200)),
                ('article', models.ForeignKey(to='extract.Article', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name_plural': 'OutLinks',
                'verbose_name': 'OutLink',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='image',
            name='alt',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
    ]
