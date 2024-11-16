# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extract', '0004_auto_20150318_0849'),
        ('web', '0003_auto_20150325_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('section_no', models.IntegerField(verbose_name='Section No.')),
                ('title', models.CharField(max_length=150, verbose_name='Section Title')),
                ('content', models.TextField(verbose_name='Section Content')),
                ('article', models.ForeignKey(to='extract.Article', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name_plural': 'Sections',
                'ordering': ['article', 'section_no'],
                'verbose_name': 'Section',
            },
            bases=(models.Model,),
        ),
    ]
