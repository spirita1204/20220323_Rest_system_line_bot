# Generated by Django 3.2.9 on 2022-04-03 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='reserve_search_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserve_search_userId', models.TextField(default='')),
                ('reserve_search_name', models.TextField(default='')),
                ('reserve_search_email', models.TextField(default='')),
                ('reserve_search_status', models.TextField(default='初始狀態')),
            ],
        ),
    ]
