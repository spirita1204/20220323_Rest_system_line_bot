# Generated by Django 3.2.9 on 2022-04-03 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0002_reserve_search_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='reserve_search_status',
            new_name='reserve_search',
        ),
    ]
