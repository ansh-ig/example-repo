# Generated by Django 5.1.2 on 2024-12-03 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_bid_alter_listing_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='tittle',
            new_name='title',
        ),
    ]
