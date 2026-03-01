from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calculus_metadata', '0002_alter_students_student_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='student_email',
            field=models.CharField(blank=True, default='', help_text='學生電子郵件', max_length=255),
        ),
    ]
