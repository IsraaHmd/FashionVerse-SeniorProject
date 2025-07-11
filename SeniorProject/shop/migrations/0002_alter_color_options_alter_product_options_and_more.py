# Generated by Django 5.1.6 on 2025-04-05 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='color',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='size',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='product',
            name='hide',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productcolor',
            name='hide',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='hide',
            field=models.BooleanField(default=False),
        ),
    ]
