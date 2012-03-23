# -*- encoding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.conf.global_settings import LANGUAGES
from django.db.models.signals import post_save

import choices
import helptexts

class AppCustomManager(models.Manager):
    """
    Domain specific model managers.
    """

    def available(self, availability=None):
        """
        Filter the queryset based on its availability.
        """
        data_queryset = super(AppCustomManager, self).get_query_set()
        if availability is not None:
            if not isinstance(availability, bool):
                data_queryset = data_queryset.filter(is_available=availability)

        return data_queryset
        
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    email = models.EmailField(_('Email'), blank=False, unique=True, null=False)

class Collection(models.Model):
    collection = models.ManyToManyField(User, related_name='user_collection',
        through='UserCollections', )
    name = models.CharField(_('Collection Name'), max_length=128, db_index=True,)
    url = models.URLField(_('Instance URL'), )
    validated = models.BooleanField(_('Validated'), default=False, )

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['name']

class UserCollections(models.Model):
    user = models.ForeignKey(User)
    collection = models.ForeignKey(Collection)
    is_default = models.BooleanField(_('Is default'), default=False, null=False, blank=False)
    is_manager = models.BooleanField(_('Is manager of the collection?'), default=False, null=False,
        blank=False)

class Institution(models.Model):

    #Custom manager
    objects = AppCustomManager()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(_('Institution Name'), max_length=128, db_index=True)
    acronym = models.CharField(_('Sigla'), max_length=16, db_index=True, blank=True)
    country = models.CharField(_('Country'), max_length=32)
    state = models.CharField(_('State'), max_length=32, null=False, blank=True,)
    city = models.CharField(_('City'), max_length=32, null=False, blank=True,)
    address = models.TextField(_('Address'), )
    address_number = models.CharField(_('Number'), max_length=8)
    address_complement = models.CharField(_('Complement'), max_length=128, null=False, blank=True,)
    zip_code = models.CharField(_('Zip Code'), max_length=16, null=True, blank=True)
    phone = models.CharField(_('Phone Number'), max_length=16, null=False, blank=True,)
    fax = models.CharField(_('Fax Number'), max_length=16, null=False, blank=True,)
    cel = models.CharField(_('Cel Number'), max_length=16, null=False, blank=True,)
    mail = models.EmailField(_('Email'),)
    validated = models.BooleanField(_('Validated'), default=False,)
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ['name']

class Publisher(Institution):
    objects = AppCustomManager()

class Journal(models.Model):

    #Custom manager
    objects = AppCustomManager()

    #Relation fields
    creator = models.ForeignKey(User, related_name='enjoy_creator', editable=False)
    publisher = models.ForeignKey('Publisher', related_name='journal_institution',null=False, help_text=helptexts.JOURNAL__PUBLISHER)
    previous_title = models.ForeignKey('Journal',related_name='prev_title', null=True, blank=True, help_text=helptexts.JOURNAL__PREVIOUS_TITLE)
    center = models.ForeignKey('Center', related_name='center_id', null=True, blank=False, help_text=helptexts.JOURNAL__CENTER)
    use_license = models.ForeignKey('UseLicense', null=True, blank=False, help_text=helptexts.JOURNAL__USE_LICENSE)
    collections = models.ManyToManyField('Collection', help_text=helptexts.JOURNAL__COLLECTIONS) #ajustar ref do help_text

    #Fields
    title = models.CharField(_('Journal Title'),max_length=256, db_index=True, help_text=helptexts.JOURNAL__TITLE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    acronym = models.CharField(_('Acronym'),max_length=8, blank=False, help_text=helptexts.JOURNAL__ACRONYM)
    scielo_issn = models.CharField(_('SciELO ISSN'),max_length=16,
        choices=choices.SCIELO_ISSN,null=False,blank=True, help_text=helptexts.JOURNAL__SCIELO_ISSN)
    print_issn = models.CharField(_('Print ISSN'),max_length=9,null=False,blank=True, help_text=helptexts.JOURNAL__PRINT_ISSN)
    eletronic_issn = models.CharField(_('Eletronic ISSN'),max_length=9,null=False,blank=True, help_text=helptexts.JOURNAL__ELETRONIC_ISSN)
    subject_descriptors = models.CharField(_('Subject / Descriptors'),max_length=512,null=False,blank=True, help_text=helptexts.JOURNAL__SUBJECT_DESCRIPTORS)
    init_year = models.CharField(_('Initial Date'),max_length=10,null=True,blank=True, help_text=helptexts.JOURNAL__INIT_YEAR)
    init_vol = models.CharField(_('Initial Volume'), max_length=4,null=False,blank=True, help_text=helptexts.JOURNAL__INIT_VOL)
    init_num = models.CharField(_('Initial Number'), max_length=4,null=False,blank=True, help_text=helptexts.JOURNAL__INIT_NUM)
    final_year = models.CharField(_('Final Date'),max_length=10,null=True,blank=True, help_text=helptexts.JOURNAL__FINAL_YEAR)
    final_vol = models.CharField(_('Final Volume'),max_length=4,null=False,blank=True, help_text=helptexts.JOURNAL__FINAL_VOL)
    final_num = models.CharField(_('Final Number'),max_length=4,null=False,blank=True, help_text=helptexts.JOURNAL__FINAL_NUM)
    frequency = models.CharField(_('Frequency'),max_length=16,
        choices=choices.FREQUENCY,null=False,blank=True, help_text=helptexts.JOURNAL__FREQUENCY)
    pub_status = models.CharField(_('Publication Status'),max_length=16,
        choices=choices.PUBLICATION_STATUS,null=False,blank=True, help_text=helptexts.JOURNAL__PUB_STATUS)
    alphabet = models.CharField(_('Alphabet'),max_length=16,
        choices=choices.ALPHABET,null=False,blank=True, help_text=helptexts.JOURNAL__ALPHABET)
    sponsor = models.CharField(_('Sponsor'), max_length=256,null=True,blank=True, help_text=helptexts.JOURNAL__SPONSOR)
    national_code = models.CharField(_('National Code'), max_length=16,null=False,blank=True, help_text=helptexts.JOURNAL__NATIONAL_CODE)
    editorial_standard = models.CharField(_('Editorial Standard'),max_length=64,
        choices=choices.STANDARD,null=False,blank=True, help_text=helptexts.JOURNAL__EDITORIAL_STANDARD)
    ctrl_vocabulary = models.CharField(_('Controlled Vocabulary'),max_length=64,
        choices=choices.CTRL_VOCABULARY,null=False,blank=True, help_text=helptexts.JOURNAL__CTRL_VOCABULARY)
    literature_type = models.CharField(_('Literature Type'),max_length=64,
        choices=choices.LITERATURE_TYPE,null=False,blank=True, help_text=helptexts.JOURNAL__LITERATURE_TYPE)
    treatment_level = models.CharField(_('Treatment Type'),max_length=64,
        choices=choices.TREATMENT_LEVEL,null=False,blank=True, help_text=helptexts.JOURNAL__TREATMENT_LEVEL)
    pub_level = models.CharField(_('Publication Level'),max_length=64,
        choices=choices.PUBLICATION_LEVEL,null=False,blank=True, help_text=helptexts.JOURNAL__PUB_LEVEL)
    secs_code = models.CharField(_('SECS Code'), max_length=64,null=False,blank=True)
    copyrighter = models.CharField(_('Copyrighter'), max_length=254, null=True, blank=True, help_text=helptexts.JOURNAL__COPYRIGHTER)
    url_main_collection = models.CharField(_('URL of main collection'), max_length=64,null=True,blank=True, help_text=helptexts.JOURNAL__URL_MAIN_COLLECTION)
    url_online_submission = models.CharField(_('URL of online submission'), max_length=64,null=True,blank=True, help_text=helptexts.JOURNAL__SUBJECT_DESCRIPTORS)
    url_journal = models.CharField(_('URL of the journal'), max_length=64,null=True,blank=True, help_text=helptexts.JOURNAL__URL_JOURNAL)
    notes = models.TextField(_('Notes'), max_length=254, null=True, blank=True, help_text=helptexts.JOURNAL__NOTES)
    validated = models.BooleanField(_('Validated'), default=False,null=False,blank=True )
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

class InstitutionCollections(models.Model):
    institution = models.ForeignKey(Institution)
    collection= models.ForeignKey(Collection, null=False)

class JournalStudyArea(models.Model):
    journal = models.ForeignKey(Journal)
    study_area = models.CharField(_('Study Area'),max_length=256,
        choices=choices.SUBJECTS,null=False,blank=True, help_text=helptexts.JOURNALSTUDYAREA__STUDYAREA)

class JournalTitle(models.Model):
    journal = models.ForeignKey(Journal)
    title = models.CharField(_('Title'), null=False, max_length=128)
    category = models.CharField(_('Title Category'), null=False, max_length=128, choices=choices.TITLE_CATEGORY)

class JournalTextLanguage(models.Model):
    journal = models.ForeignKey(Journal)
    language = models.CharField(_('Text Languages'),max_length=64,choices=LANGUAGES,blank=True,null=False)

class JournalHist(models.Model):
    journal = models.ForeignKey(Journal)
    date = models.DateField(_('Date'), editable=True, blank=True)
    status = models.CharField(_('Status'), choices=choices.JOURNAL_HIST_STATUS, null=False, blank=True, max_length=2)

class JournalMission(models.Model):
    journal = models.ForeignKey(Journal, null=False)
    description = models.TextField(_('Mission'), null=False, help_text=helptexts.JOURNALMISSION_DESCRIPTION)
    language = models.CharField(_('Language'), null=False, max_length=128, choices=LANGUAGES)

class IndexDatabase(models.Model):
    name = models.CharField(_('Database Name'), max_length=256, null=False, blank=True)

    def __unicode__(self):
        return self.name

class JournalIndexCoverage(models.Model):
    journal = models.ForeignKey(Journal)
    database = models.ForeignKey(IndexDatabase, null=True, help_text=helptexts.JOURNALINDEXCOVERAGE__DATABASE)
    title = models.CharField(_('Title'), max_length=256, null=False, blank=True)
    identify = models.CharField(_('Identify'), max_length=256, null=False, blank=True)

class UseLicense(models.Model):
    license_code = models.CharField(_('License Code'), unique=True, null=False, blank=False, max_length=64)
    reference_url = models.URLField(_('License Reference URL'), null=True, blank=True)
    disclaimer = models.TextField(_('Disclaimer'), null=True, blank=True, max_length=512)

    def __unicode__(self):
        return self.license_code

class TranslatedData(models.Model):
    translation = models.CharField(_('Translation'), null=True, blank=True, max_length=512)
    language = models.CharField(_('Language'), choices=choices.LANGUAGE, null=False, blank=False, max_length=32)
    model = models.CharField(_('Model'), null=False, blank=False, max_length=32)
    field = models.CharField(_('Field'), null=False, blank=False, max_length=32)

    def __unicode__(self):
        return self.translation if self.translation is not None else 'Missing trans: {0}.{1}'.format(self.model, self.field)

class Section(models.Model):
    #Custom manager
    objects = AppCustomManager()

    title = models.CharField(_('Title'), null=False, blank=False, max_length=256)
    title_translations = models.ManyToManyField(TranslatedData, null=True, blank=True,)
    journal = models.ForeignKey(Journal, null=True, blank=True)
    code = models.CharField(_('Code'), null=True, blank=True, max_length=16)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=False)

    def __unicode__(self):
        return self.title

class Issue(models.Model):

    #Custom manager
    objects = AppCustomManager()

    section = models.ManyToManyField(Section)
    journal = models.ForeignKey(Journal, null=True, blank=False)
    title = models.CharField(_('Title'), null=True, blank=True, max_length=256)
    volume = models.CharField(_('Volume'), null=True, blank=True, max_length=16)
    number = models.CharField(_('Number'), null=True, blank=True, max_length=16)
    is_press_release = models.BooleanField(_('Is Press Release?'), default=False, null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publication_date = models.DateField(null=False, blank=False)
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=True) #status v42
    is_marked_up = models.BooleanField(_('Is Marked Up?'), default=False, null=False, blank=True) #v200
    bibliographic_strip = models.CharField(_('Custom Bibliographic Strip'), null=True, blank=True, max_length=128) #l10n
    use_license = models.ForeignKey(UseLicense, null=True)
    publisher_fullname = models.CharField(_('Publisher Full Name'), null=True, blank=True, max_length=128)
    total_documents = models.IntegerField(_('Total of Documents'), null=False, blank=False, default=0)
    ctrl_vocabulary = models.CharField(_('Controlled Vocabulary'), max_length=64,
        choices=choices.CTRL_VOCABULARY, null=False, blank=True)
    editorial_standard = models.CharField(_('Editorial Standard'), max_length=64,
        choices=choices.STANDARD, null=False, blank=True)

    def identification(self):

        if self.number is not None:
            n = self.number
            if n != 'ahead' and n != 'review':
                n ='(' + self.number + ')'
            else:
                n = self.number

            return self.volume + ' ' + n
        else:
            return ''

    def __unicode__(self):
        return self.identification()

class Supplement(Issue):
    suppl_label = models.CharField(_('Supplement Label'), null=True, blank=True, max_length=256)

class Center(Institution):
    objects = AppCustomManager()

