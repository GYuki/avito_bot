# Generated by Django 2.0 on 2018-05-12 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parserapp', '0004_category_cmd'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='url',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
