from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.base.models import PasskeyCredential


class PasskeyRegisterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='passkey-user',
            email='passkey@example.com',
            password='secret',
        )

    def test_register_begin_requires_auth(self):
        response = self.client.post('/api/v2/passkey/register/begin/')
        self.assertEqual(response.status_code, 401)

    def test_register_begin_returns_options_and_sets_session_challenge(self):
        self.client.force_login(self.user)
        response = self.client.post('/api/v2/passkey/register/begin/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('options', data)
        self.assertIn('challenge', data['options'])
        # Session must have the challenge
        session = self.client.session
        self.assertIn('_webauthn_registration_challenge', session)

    def test_register_complete_without_challenge_returns_400(self):
        self.client.force_login(self.user)
        response = self.client.post(
            '/api/v2/passkey/register/complete/',
            data=json.dumps({'name': 'Test Key', 'credential': {}}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    @patch('rockon.api.endpoints.passkey.webauthn.verify_registration_response')
    def test_register_complete_saves_credential(self, mock_verify):
        self.client.force_login(self.user)
        # Set up a fake challenge in the session
        session = self.client.session
        session['_webauthn_registration_challenge'] = (
            'dGVzdGNoYWxsZW5nZQ'  # base64url "testchallenge"
        )
        session.save()

        mock_result = MagicMock()
        mock_result.credential_id = b'test-credential-id'
        mock_result.credential_public_key = b'fake-cose-key'
        mock_result.sign_count = 0
        mock_result.aaguid = None
        mock_verify.return_value = mock_result

        response = self.client.post(
            '/api/v2/passkey/register/complete/',
            data=json.dumps({'name': 'My Key', 'credential': {'type': 'public-key'}}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(PasskeyCredential.objects.filter(user=self.user).exists())

    @patch('rockon.api.endpoints.passkey.webauthn.verify_registration_response')
    def test_register_complete_rejects_duplicate_credential(self, mock_verify):
        self.client.force_login(self.user)
        session = self.client.session
        session['_webauthn_registration_challenge'] = 'dGVzdGNoYWxsZW5nZQ'
        session.save()

        mock_result = MagicMock()
        mock_result.credential_id = b'dupe-credential-id'
        mock_result.credential_public_key = b'fake-cose-key'
        mock_result.sign_count = 0
        mock_result.aaguid = None
        mock_verify.return_value = mock_result

        # Pre-create a credential with the same ID that mock will return
        import base64

        cred_id = base64.urlsafe_b64encode(b'dupe-credential-id').decode().rstrip('=')
        PasskeyCredential.objects.create(
            user=self.user,
            credential_id=cred_id,
            public_key=b'key',
            sign_count=0,
        )

        response = self.client.post(
            '/api/v2/passkey/register/complete/',
            data=json.dumps({'name': '', 'credential': {'type': 'public-key'}}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('already registered', response.json()['message'])


class PasskeyAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='auth-passkey-user',
            email='authpasskey@example.com',
            password='secret',
        )
        self.credential_id = 'dGVzdC1jcmVk'  # base64url "test-cred"
        PasskeyCredential.objects.create(
            user=self.user,
            credential_id=self.credential_id,
            public_key=b'fake-public-key',
            sign_count=0,
        )

    def test_auth_begin_returns_options_without_auth(self):
        response = self.client.post('/api/v2/passkey/auth/begin/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('options', data)
        self.assertIn('challenge', data['options'])

    def test_auth_begin_sets_session_challenge(self):
        self.client.post('/api/v2/passkey/auth/begin/')
        session = self.client.session
        self.assertIn('_webauthn_authentication_challenge', session)

    def test_auth_complete_without_challenge_returns_400(self):
        response = self.client.post(
            '/api/v2/passkey/auth/complete/',
            data=json.dumps({'credential': {'id': self.credential_id}}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_auth_complete_unknown_credential_returns_403(self):
        session = self.client.session
        session['_webauthn_authentication_challenge'] = 'dGVzdGNoYWxsZW5nZQ'
        session.save()

        response = self.client.post(
            '/api/v2/passkey/auth/complete/',
            data=json.dumps({'credential': {'id': 'nonexistent-credential'}}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    @patch('rockon.api.endpoints.passkey.webauthn.verify_authentication_response')
    def test_auth_complete_updates_sign_count_and_last_used(self, mock_verify):
        session = self.client.session
        session['_webauthn_authentication_challenge'] = 'dGVzdGNoYWxsZW5nZQ'
        session.save()

        mock_result = MagicMock()
        mock_result.new_sign_count = 7
        mock_verify.return_value = mock_result

        response = self.client.post(
            '/api/v2/passkey/auth/complete/',
            data=json.dumps(
                {'credential': {'id': self.credential_id, 'rawId': self.credential_id}}
            ),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        # Credential counters and timestamp updated
        cred = PasskeyCredential.objects.get(credential_id=self.credential_id)
        self.assertEqual(cred.sign_count, 7)
        self.assertIsNotNone(cred.last_used_at)


class PasskeyManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='mgmt-passkey-user',
            email='mgmt@example.com',
            password='secret',
        )
        self.other_user = User.objects.create_user(
            username='other-passkey-user',
            email='other-pk@example.com',
            password='secret',
        )
        self.credential = PasskeyCredential.objects.create(
            user=self.user,
            credential_id='bXlLZXk',
            public_key=b'public-key-data',
            sign_count=5,
            name='My Phone',
        )
        self.other_credential = PasskeyCredential.objects.create(
            user=self.other_user,
            credential_id='b3RoZXJLZXk',
            public_key=b'other-public-key',
            sign_count=0,
            name='Other Phone',
        )

    def test_list_requires_auth(self):
        response = self.client.get('/api/v2/passkey/')
        self.assertEqual(response.status_code, 401)

    def test_list_returns_only_own_passkeys(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/v2/passkey/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['passkeys']), 1)
        self.assertEqual(data['passkeys'][0]['name'], 'My Phone')

    def test_delete_requires_auth(self):
        response = self.client.delete(f'/api/v2/passkey/{self.credential.id}/')
        self.assertEqual(response.status_code, 401)

    def test_delete_own_passkey_succeeds(self):
        self.client.force_login(self.user)
        response = self.client.delete(f'/api/v2/passkey/{self.credential.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            PasskeyCredential.objects.filter(id=self.credential.id).exists()
        )

    def test_delete_other_users_passkey_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.delete(f'/api/v2/passkey/{self.other_credential.id}/')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            PasskeyCredential.objects.filter(id=self.other_credential.id).exists()
        )
