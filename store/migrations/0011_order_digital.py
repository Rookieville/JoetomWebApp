# Generated by Django 3.2.15 on 2022-08-30 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_customer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='digital',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
