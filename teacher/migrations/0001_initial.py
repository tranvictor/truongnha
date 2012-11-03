# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Teacher'
        db.create_table('personal_teacher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True)),
            ('home_town', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(default='Nam', max_length=10)),
            ('sms_phone', self.gf('django.db.models.fields.CharField')(max_length=13, blank=True)),
            ('current_address', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='teachers', unique=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('personal', ['Teacher'])

        # Adding model 'Class'
        db.create_table('personal_class', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('teacher_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Teacher'], null=True, blank=True)),
        ))
        db.send_create_signal('personal', ['Class'])

        # Adding model 'Student'
        db.create_table('personal_student', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True)),
            ('home_town', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(default='Nam', max_length=10)),
            ('sms_phone', self.gf('django.db.models.fields.CharField')(max_length=13, blank=True)),
            ('current_address', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('father_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('father_phone', self.gf('django.db.models.fields.CharField')(max_length=13, null=True, blank=True)),
            ('mother_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('mother_phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('current_status', self.gf('django.db.models.fields.CharField')(default='OK', max_length=200, null=True, blank=True)),
            ('user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('personal', ['Student'])

        # Adding model 'Attend'
        db.create_table('personal_attend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pupil', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Student'])),
            ('_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Class'])),
            ('attend_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('leave_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('is_member', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('personal', ['Attend'])

        # Adding model 'Mark'
        db.create_table('personal_mark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('diem', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hs', self.gf('django.db.models.fields.FloatField')()),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('class_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Class'])),
            ('student_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Student'])),
        ))
        db.send_create_signal('personal', ['Mark'])

        # Adding model 'Note'
        db.create_table('personal_note', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('class_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Class'])),
            ('student_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Student'])),
        ))
        db.send_create_signal('personal', ['Note'])

        # Adding model 'Receivables'
        db.create_table('personal_receivables', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('amount', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('class_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Class'])),
        ))
        db.send_create_signal('personal', ['Receivables'])

        # Adding model 'Payment'
        db.create_table('personal_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('receivables_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Class'])),
            ('student_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.Student'])),
        ))
        db.send_create_signal('personal', ['Payment'])


    def backwards(self, orm):
        # Deleting model 'Teacher'
        db.delete_table('personal_teacher')

        # Deleting model 'Class'
        db.delete_table('personal_class')

        # Deleting model 'Student'
        db.delete_table('personal_student')

        # Deleting model 'Attend'
        db.delete_table('personal_attend')

        # Deleting model 'Mark'
        db.delete_table('personal_mark')

        # Deleting model 'Note'
        db.delete_table('personal_note')

        # Deleting model 'Receivables'
        db.delete_table('personal_receivables')

        # Deleting model 'Payment'
        db.delete_table('personal_payment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'personal.attend': {
            'Meta': {'object_name': 'Attend'},
            '_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Class']"}),
            'attend_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_member': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'leave_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'pupil': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Student']"})
        },
        'personal.class': {
            'Meta': {'object_name': 'Class'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'teacher_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Teacher']", 'null': 'True', 'blank': 'True'})
        },
        'personal.mark': {
            'Meta': {'object_name': 'Mark'},
            'class_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Class']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'diem': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hs': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Student']"})
        },
        'personal.note': {
            'Meta': {'object_name': 'Note'},
            'class_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Class']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Student']"})
        },
        'personal.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'receivables_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Class']"}),
            'student_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Student']"})
        },
        'personal.receivables': {
            'Meta': {'object_name': 'Receivables'},
            'amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'class_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personal.Class']"}),
            'deadline': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'personal.student': {
            'Meta': {'object_name': 'Student'},
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'student_set'", 'symmetrical': 'False', 'through': "orm['personal.Attend']", 'to': "orm['personal.Class']"}),
            'current_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'current_status': ('django.db.models.fields.CharField', [], {'default': "'OK'", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'father_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'father_phone': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'home_town': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mother_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'mother_phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "'Nam'", 'max_length': '10'}),
            'sms_phone': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'personal.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'current_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'home_town': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "'Nam'", 'max_length': '10'}),
            'sms_phone': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'teachers'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['personal']