# Generated by Django 3.1.13 on 2021-07-12 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0005_orderlineitem_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderlineitem',
            name='image_url',
        ),
    ]
