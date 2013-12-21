# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'SurveyChartPlugin'
        db.delete_table('cmsplugin_surveychartplugin')

        # Adding model 'Intake2'
        db.create_table('pollster_intake2', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('global_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('channel', self.gf('django.db.models.fields.CharField')(max_length=36, null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('TITLE_1', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('NOTE_1', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('NOTE_2', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('TITLE_2', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('QUESTION_1', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('TITLE_3', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('pollster', ['Intake2'])


    def backwards(self, orm):
        
        # Adding model 'SurveyChartPlugin'
        db.create_table('cmsplugin_surveychartplugin', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pollster.Chart'])),
        ))
        db.send_create_signal('pollster', ['SurveyChartPlugin'])

        # Deleting model 'Intake2'
        db.delete_table('pollster_intake2')


    models = {
        'pollster.chart': {
            'Meta': {'ordering': "['survey', 'shortname']", 'unique_together': "(('survey', 'shortname'),)", 'object_name': 'Chart'},
            'chartwrapper': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'geotable': ('django.db.models.fields.CharField', [], {'default': "'pollster_zip_codes'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'sqlfilter': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '255'}),
            'sqlsource': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.ChartType']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'pollster.charttype': {
            'Meta': {'object_name': 'ChartType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'pollster.intake2': {
            'Meta': {'object_name': 'Intake2'},
            'NOTE_1': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'NOTE_2': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'QUESTION_1': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'TITLE_1': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'TITLE_2': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'TITLE_3': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True'}),
            'global_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'pollster.option': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'Option'},
            'clone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Option']", 'null': 'True', 'blank': 'True'}),
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionColumn']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Question']"}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionRow']", 'null': 'True', 'blank': 'True'}),
            'starts_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4095', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'virtual_inf': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_regex': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_sup': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.VirtualOptionType']", 'null': 'True', 'blank': 'True'})
        },
        'pollster.question': {
            'Meta': {'ordering': "['survey', 'ordinal']", 'object_name': 'Question'},
            'data_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionDataType']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'error_message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'open_option_data_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'questions_with_open_option'", 'null': 'True', 'to': "orm['pollster.QuestionDataType']"}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'regex': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1023', 'blank': 'True'}),
            'starts_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'tags': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questioncolumn': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'QuestionColumn'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'column_set'", 'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questiondatatype': {
            'Meta': {'object_name': 'QuestionDataType'},
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questionrow': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'QuestionRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'row_set'", 'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sufficient': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'object_options': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'object_of_rules'", 'symmetrical': 'False', 'to': "orm['pollster.Option']"}),
            'object_question': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'object_of_rules'", 'null': 'True', 'to': "orm['pollster.Question']"}),
            'rule_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.RuleType']"}),
            'subject_options': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subject_of_rules'", 'symmetrical': 'False', 'to': "orm['pollster.Option']"}),
            'subject_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subject_of_rules'", 'to': "orm['pollster.Question']"})
        },
        'pollster.ruletype': {
            'Meta': {'object_name': 'RuleType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.survey': {
            'Meta': {'object_name': 'Survey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']", 'null': 'True', 'blank': 'True'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'db_index': 'True', 'blank': 'True'})
        },
        'pollster.translationoption': {
            'Meta': {'ordering': "['translation', 'option']", 'unique_together': "(('translation', 'option'),)", 'object_name': 'TranslationOption'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Option']"}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4095', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestion': {
            'Meta': {'ordering': "['translation', 'question']", 'unique_together': "(('translation', 'question'),)", 'object_name': 'TranslationQuestion'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'error_message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestioncolumn': {
            'Meta': {'ordering': "['translation', 'column']", 'unique_together': "(('translation', 'column'),)", 'object_name': 'TranslationQuestionColumn'},
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionColumn']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestionrow': {
            'Meta': {'ordering': "['translation', 'row']", 'unique_together': "(('translation', 'row'),)", 'object_name': 'TranslationQuestionRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionRow']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationsurvey': {
            'Meta': {'ordering': "['survey', 'language']", 'unique_together': "(('survey', 'language'),)", 'object_name': 'TranslationSurvey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.virtualoptiontype': {
            'Meta': {'object_name': 'VirtualOptionType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'question_data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionDataType']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['pollster']
