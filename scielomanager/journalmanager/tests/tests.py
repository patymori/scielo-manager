# coding:utf-8
"""
Use this module to write functional tests for the view-functions, only!
"""
from django_webtest import WebTest
from django.core.urlresolvers import reverse
from django_factory_boy import auth

from journalmanager.tests import modelfactories


HASH_FOR_123 = 'sha1$93d45$5f366b56ce0444bfea0f5634c7ce8248508c9799'


def _makePermission(perm, model, app_label='journalmanager'):
    """
    Retrieves a Permission according to the given model and app_label.
    """
    from django.contrib.contenttypes import models
    from django.contrib.auth import models as auth_models

    ct = models.ContentType.objects.get(model=model,
                                        app_label=app_label)
    return auth_models.Permission.objects.get(codename=perm, content_type=ct)


class LoginFormTests(WebTest):

    def _makePermission(self, perm, model, app_label='journalmanager'):
        """
        Retrieves a ContentType according to the given model and app_label.
        """
        from django.contrib.contenttypes import models
        from django.contrib.auth import models as auth_models

        ct = models.ContentType.objects.get(model=model,
                                            app_label=app_label)
        return auth_models.Permission.objects.get(codename=perm, content_type=ct)

    def test_the_user_must_provide_his_credentials(self):
        form = self.app.get(reverse('journalmanager.user_login')).forms[0]
        form['username'] = ''
        form['password'] = ''
        response = form.submit()

        self.assertTrue('error' in response.body)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_right_username_and_wrong_password(self):
        user = auth.UserF(username='foo',
                          password=HASH_FOR_123,
                          is_active=True)

        form = self.app.get(reverse('journalmanager.user_login')).forms[0]
        form['username'] = 'foo'
        form['password'] = 'baz'
        response = form.submit()

        self.assertTrue('error' in response.body)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_wrong_username_and_right_password(self):
        user = auth.UserF(username='foo',
                          password=HASH_FOR_123,
                          is_active=True)

        form = self.app.get(reverse('journalmanager.user_login')).forms[0]
        form['username'] = 'fuu'
        form['password'] = '123'
        response = form.submit()

        self.assertTrue('error' in response.body)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_right_username_and_right_password(self):
        user = auth.UserF(username='foo',
                          password=HASH_FOR_123,
                          is_active=True)

        collection = modelfactories.CollectionFactory.create()
        collection.add_user(user)

        form = self.app.get(reverse('journalmanager.user_login')).forms[0]
        form['username'] = 'foo'
        form['password'] = '123'

        response = form.submit().follow()

        self.assertTemplateUsed(response, 'journalmanager/home_journal.html')

    def test_right_username_and_right_password_for_inactive_user(self):
        user = auth.UserF(username='foo',
                          password=HASH_FOR_123,
                          is_active=False)

        collection = modelfactories.CollectionFactory.create()
        collection.add_user(user)

        form = self.app.get(reverse('journalmanager.user_login')).forms[0]
        form['username'] = 'foo'
        form['password'] = '123'

        response = form.submit()

        self.assertTrue('error' in response.body)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_redirect_to_restricted_page_after_successful_login(self):
        user = auth.UserF(is_active=True)
        perm = _makePermission(perm='list_journal', model='journal')
        user.user_permissions.add(perm)

        collection = modelfactories.CollectionFactory.create()
        collection.add_user(user)

        page = self.app.get(reverse('journal.index'), user=user)

        page.mustcontain('no items')


class SectionFormTests(WebTest):

    def setUp(self):
        self.user = auth.UserF(is_active=True)

        self.collection = modelfactories.CollectionFactory.create()
        self.collection.add_user(self.user)

    def test_basic_structure(self):
        perm = _makePermission(perm='change_section', model='section')
        self.user.user_permissions.add(perm)

        journal = modelfactories.JournalFactory(collection=self.collection)
        form = self.app.get(reverse('section.add', args=[journal.pk]),
            user=self.user)

        self.assertTemplateUsed(form, 'journalmanager/add_section.html')
        form.mustcontain('section-form',
                         'csrfmiddlewaretoken',
                         'titles-TOTAL_FORMS',
                         'titles-INITIAL_FORMS',
                         'titles-MAX_NUM_FORMS',
                        )

    def test_POST_workflow_with_valid_formdata(self):
        perm1 = _makePermission(perm='change_section', model='section')
        self.user.user_permissions.add(perm1)
        perm2 = _makePermission(perm='list_section', model='section')
        self.user.user_permissions.add(perm2)

        journal = modelfactories.JournalFactory(collection=self.collection)
        language = modelfactories.LanguageFactory.create(iso_code='en', name='english')
        journal.languages.add(language)

        form = self.app.get(reverse('section.add', args=[journal.pk]),
            user=self.user).forms['section-form']

        form['titles-0-title'] = 'Original Article'
        form.set('titles-0-language', '1')

        response = form.submit().follow()

        self.assertTemplateUsed(response, 'journalmanager/section_dashboard.html')
        response.mustcontain('Original Article')

    def test_POST_workflow_with_invalid_formdata(self):
        perm = _makePermission(perm='change_section', model='section')
        self.user.user_permissions.add(perm)

        journal = modelfactories.JournalFactory(collection=self.collection)
        language = modelfactories.LanguageFactory.create(iso_code='en', name='english')
        journal.languages.add(language)

        form = self.app.get(reverse('section.add', args=[journal.pk]),
            user=self.user).forms['section-form']

        response = form.submit()

        response.mustcontain('There are some errors or missing data')
