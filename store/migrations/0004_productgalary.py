# Generated by Django 3.2 on 2021-06-01 03:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductGalary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='store/product')),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]
