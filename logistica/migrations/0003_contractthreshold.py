from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0002_logisticaconfiguration_aa_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractThreshold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Contract title to match against.', max_length=255)),
                ('match_type', models.CharField(
                    choices=[('exact', 'Exact match'), ('contains', 'Contains')],
                    default='exact',
                    help_text='How to compare the title against contract names.',
                    max_length=10,
                )),
                ('minimum_count', models.PositiveIntegerField(help_text='Minimum number of outstanding contracts expected.')),
            ],
            options={
                'ordering': ['title'],
                'permissions': [('manage_contract_thresholds', 'Can manage contract thresholds')],
            },
        ),
    ]
