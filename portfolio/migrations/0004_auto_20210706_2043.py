# Generated by Django 3.1.7 on 2021-07-06 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_product_friendly_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='complete',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='user_name',
            field=models.CharField(default='username', max_length=254),
        ),
    ]