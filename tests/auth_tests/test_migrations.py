from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from .models import Proxy, UserProxy

update_proxy_permissions = import_module('django.contrib.auth.migrations.0011_update_proxy_permissions')


class ProxyModelWithDifferentAppLabelTests(TestCase):
    available_apps = [
        'auth_tests',
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]

    def setUp(self):
        """
        Create proxy permissions with content_type to the concrete model
        rather than the proxy model (as they were before Django 2.2 and
        migration 11).
        """
        Permission.objects.all().delete()
        self.concrete_content_type = ContentType.objects.get_for_model(UserProxy)
        self.default_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='add_userproxy',
            name='Can add userproxy',
        )
        self.custom_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='use_different_app_label',
            name='May use a different app label',
        )

    def test_proxy_model_permissions_contenttype(self):
        proxy_model_content_type = ContentType.objects.get_for_model(UserProxy, for_concrete_model=False)
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        self.default_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, proxy_model_content_type)
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.custom_permission.content_type, proxy_model_content_type)

    def test_user_has_now_proxy_model_permissions(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth.' + permission.codename))
            self.assertFalse(user.has_perm('auth_tests.' + permission.codename))
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertFalse(user.has_perm('auth.' + permission.codename))
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))

    def test_migrate_backwards(self):
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        update_proxy_permissions.revert_proxy_model_permissions(apps, None)
        self.default_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)

    def test_user_keeps_same_permissions_after_migrating_backward(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth.' + permission.codename))
            self.assertFalse(user.has_perm('auth_tests.' + permission.codename))
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        update_proxy_permissions.revert_proxy_model_permissions(apps, None)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth.' + permission.codename))
            self.assertFalse(user.has_perm('auth_tests.' + permission.codename))


class ProxyModelWithSameAppLabelTests(TestCase):
    available_apps = [
        'auth_tests',
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]

    def setUp(self):
        """
        Create proxy permissions with content_type to the concrete model
        rather than the proxy model (as they were before Django 2.2 and
        migration 11).
        """
        Permission.objects.all().delete()
        self.concrete_content_type = ContentType.objects.get_for_model(Proxy)
        self.default_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='add_proxy',
            name='Can add proxy',
        )
        self.custom_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='display_proxys',
            name='May display proxys information',
        )

    def test_proxy_model_permissions_contenttype(self):
        proxy_model_content_type = ContentType.objects.get_for_model(Proxy, for_concrete_model=False)
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        self.default_permission.refresh_from_db()
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, proxy_model_content_type)
        self.assertEqual(self.custom_permission.content_type, proxy_model_content_type)

    def test_user_still_has_proxy_model_permissions(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))

    def test_migrate_backwards(self):
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        update_proxy_permissions.revert_proxy_model_permissions(apps, None)
        self.default_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)

    def test_user_keeps_same_permissions_after_migrating_backward(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))
        update_proxy_permissions.update_proxy_model_permissions(apps, None)
        update_proxy_permissions.revert_proxy_model_permissions(apps, None)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))
