from django.db import migrations

def add_default_categories(apps, schema_editor):
    Category = apps.get_model('contacts', 'Category')
    defaults = [
        ('Friend', 'Personal friend'),
        ('Family', 'Family member'),
        ('Roommate', 'Lives with you'),
        ('Doctor', 'Medical contact'),
        ('Police', 'Emergency services'),
        ('Other', 'Other contact'),
    ]
    for name, desc in defaults:
        Category.objects.get_or_create(name=name, defaults={'description': desc})

class Migration(migrations.Migration):
    dependencies = [
        ('contacts', '0002_remove_contact_latitude_remove_contact_longitude'),
    ]
    operations = [
        migrations.RunPython(add_default_categories),
    ]
