# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-28 22:14
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0055_auto_20160528_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentSearchFormModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100)),
                ('grade_level_wanted', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Freshman', 'Freshman'), ('Sophomore', 'Sophomore'), ('Junior', 'Junior'), ('Senior', 'Senior'), ('Graduate', 'Graduate'), ('PhD', 'PhD')], max_length=45)),
                ('major_wanted', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Aeronautical Engineering', 'Aeronautical Engineering'), ('Applied Physics', 'Applied Physics'), ('Architecture', 'Architecture'), ('Biochemistry and Biophysics', 'Biochemistry and Biophysics'), ('Bioinformatics and Molecular Biology', 'Bioinformatics and Molecular Biology'), ('Biology', 'Biology'), ('Biomedical Engineering', 'Biomedical Engineering'), ('Building Science', 'Building Science'), ('Business and Management', 'Business and Management'), ('Chemical Engineering', 'Chemical Engineering'), ('Chemistry', 'Chemistry'), ('Civil Engineering', 'Civil Engineering'), ('Cognitive Science', 'Cognitive Science'), ('Communication', 'Communication'), ('Computer and Systems Engineering', 'Computer and Systems Engineering'), ('Computer Science', 'Computer Science'), ('Design, Innovation, and Society', 'Design, Innovation, and Society'), ('Economics', 'Economics'), ('Electrical Engineering', 'Electrical Engineering'), ('Electronic Arts', 'Electronic Arts'), ('Electronic Media, Arts, and Communication', 'Electronic Media, Arts, and Communication'), ('Environmental Engineering', 'Environmental Engineering'), ('Environmental Science', 'Environmental Science'), ('Games and Simulation Arts and Sciences', 'Games and Simulation Arts and Sciences'), ('Geology', 'Geology'), ('Hydrogeology', 'Hydrogeology'), ('Industrial and Management Engineering', 'Industrial and Management Engineering'), ('Information Technology and Web Science', 'Information Technology and Web Science'), ('Interdisciplinary Science', 'Interdisciplinary Science'), ('Materials Engineering', 'Materials Engineering'), ('Mathematics', 'Mathematics'), ('Mechanical Engineering', 'Mechanical Engineering'), ('Nuclear Engineering', 'Nuclear Engineering'), ('Philosophy', 'Philosophy'), ('Physics', 'Physics'), ('Psychology', 'Psychology'), ('Science, Technology, and Society', 'Science, Technology, and Society'), ('Sustainability Studies', 'Sustainability Studies')], max_length=818)),
                ('open_to_relocation', models.BooleanField(default=False)),
                ('GPA', models.DecimalField(decimal_places=2, max_digits=3, null=True)),
            ],
        ),
    ]