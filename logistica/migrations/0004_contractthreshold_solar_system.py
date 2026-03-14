from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corptools', '0126_assetsfilter_reversed_logic'),
        ('logistica', '0003_contractthreshold'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractthreshold',
            name='solar_system',
            field=models.ForeignKey(
                help_text='Solar system the contract must originate from.',
                on_delete=django.db.models.deletion.CASCADE,
                to='corptools.mapsystem',
            ),
            preserve_default=False,
        ),
    ]
