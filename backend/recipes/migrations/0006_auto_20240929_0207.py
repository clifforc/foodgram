# Generated by Django 3.2.3 on 2024-09-28 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_short_link'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='shoppingcart',
            unique_together=set(),
        ),
    ]
