# Generated by Django 3.0.5 on 2021-11-08 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20211108_1058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pk',)},
        ),
    ]
