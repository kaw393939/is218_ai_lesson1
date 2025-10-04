"""
Tests for Lesson 2.4: Secure Logging - Protecting Sensitive Data

This module tests the implementation of logging filters that automatically
redact sensitive information like passwords, API keys, credit card numbers,
and personally identifiable information (PII).
"""

import logging


class TestImports:
    """Test that all required components can be imported."""

    def test_import_sensitive_data_filter(self):
        """Test that SensitiveDataFilter class exists."""
        from logger import SensitiveDataFilter
        assert SensitiveDataFilter is not None

    def test_import_get_secure_logger(self):
        """Test that get_secure_logger function exists."""
        from logger import get_secure_logger
        assert callable(get_secure_logger)

    def test_import_sanitize_dict(self):
        """Test that sanitize_dict function exists."""
        from logger import sanitize_dict
        assert callable(sanitize_dict)

    def test_import_mask_credit_card(self):
        """Test that mask_credit_card function exists."""
        from logger import mask_credit_card
        assert callable(mask_credit_card)

    def test_import_mask_email(self):
        """Test that mask_email function exists."""
        from logger import mask_email
        assert callable(mask_email)


class TestSensitiveDataFilter:
    """Test the SensitiveDataFilter class."""

    def test_filter_has_patterns(self):
        """Test that filter has PATTERNS class variable."""
        from logger import SensitiveDataFilter
        assert hasattr(SensitiveDataFilter, 'PATTERNS')
        assert isinstance(SensitiveDataFilter.PATTERNS, dict)

    def test_filter_has_filter_method(self):
        """Test that filter has filter method."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        assert hasattr(filter_obj, 'filter')
        assert callable(filter_obj.filter)

    def test_filter_has_redact_method(self):
        """Test that filter has redact method."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        assert hasattr(filter_obj, 'redact')
        assert callable(filter_obj.redact)

    def test_redact_credit_card(self):
        """Test that credit card numbers are redacted."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "Payment made with card 4532-1234-5678-9010"
        redacted = filter_obj.redact(text)
        assert '4532-1234-5678-9010' not in redacted
        assert '[REDACTED-CC]' in redacted

    def test_redact_credit_card_no_dashes(self):
        """Test that credit card without dashes is redacted."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "Card number: 4532123456789010"
        redacted = filter_obj.redact(text)
        assert '4532123456789010' not in redacted
        assert '[REDACTED-CC]' in redacted

    def test_redact_ssn(self):
        """Test that social security numbers are redacted."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "SSN: 123-45-6789"
        redacted = filter_obj.redact(text)
        assert '123-45-6789' not in redacted
        assert '[REDACTED-SSN]' in redacted

    def test_redact_email(self):
        """Test that email addresses are redacted."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "Contact: user@example.com"
        redacted = filter_obj.redact(text)
        assert 'user@example.com' not in redacted
        assert '[REDACTED-EMAIL]' in redacted

    def test_redact_api_key(self):
        """Test that API keys are redacted."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "Using api_key=sk_live_abc123xyz"
        redacted = filter_obj.redact(text)
        assert 'sk_live_abc123xyz' not in redacted
        assert '[REDACTED-KEY]' in redacted

    def test_redact_password(self):
        """Test that passwords are redacted."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "Login with password=super_secret_123"
        redacted = filter_obj.redact(text)
        assert 'super_secret_123' not in redacted
        assert '[REDACTED-PWD]' in redacted

    def test_redact_multiple_patterns(self):
        """Test that multiple patterns are redacted in one message."""
        from logger import SensitiveDataFilter
        filter_obj = SensitiveDataFilter()
        text = "User user@example.com paid with card 4532123456789010 using api_key=abc123"
        redacted = filter_obj.redact(text)
        assert 'user@example.com' not in redacted
        assert '4532123456789010' not in redacted
        assert 'abc123' not in redacted
        assert '[REDACTED-EMAIL]' in redacted
        assert '[REDACTED-CC]' in redacted
        assert '[REDACTED-KEY]' in redacted


class TestGetSecureLogger:
    """Test the get_secure_logger function."""

    def test_returns_logger(self):
        """Test that function returns a Logger instance."""
        from logger import get_secure_logger
        logger = get_secure_logger('test_secure_logger_returns')
        assert isinstance(logger, logging.Logger)

    def test_logger_has_filter(self):
        """Test that returned logger has SensitiveDataFilter attached."""
        from logger import get_secure_logger, SensitiveDataFilter
        logger = get_secure_logger('test_secure_logger_filter')
        # Check if any filter is a SensitiveDataFilter
        has_sensitive_filter = any(
            isinstance(f, SensitiveDataFilter) for f in logger.filters
        )
        assert has_sensitive_filter

    def test_logger_redacts_in_practice(self, caplog):
        """Test that logger actually redacts sensitive data."""
        from logger import get_secure_logger
        logger = get_secure_logger('test_secure_logger_practice')
        
        with caplog.at_level(logging.INFO, logger='test_secure_logger_practice'):
            logger.info("Credit card: 4532-1234-5678-9010")
        
        # Check that the credit card was redacted in the captured logs
        assert '4532-1234-5678-9010' not in caplog.text
        assert '[REDACTED-CC]' in caplog.text


class TestSanitizeDict:
    """Test the sanitize_dict function."""

    def test_sanitize_password_key(self):
        """Test that password key is redacted."""
        from logger import sanitize_dict
        data = {'username': 'john', 'password': 'secret123'}
        sanitized = sanitize_dict(data)
        assert sanitized['password'] == '[REDACTED]'
        assert sanitized['username'] == 'john'

    def test_sanitize_api_key(self):
        """Test that api_key is redacted."""
        from logger import sanitize_dict
        data = {'service': 'stripe', 'api_key': 'sk_live_abc123'}
        sanitized = sanitize_dict(data)
        assert sanitized['api_key'] == '[REDACTED]'
        assert sanitized['service'] == 'stripe'

    def test_sanitize_case_insensitive(self):
        """Test that sanitization is case-insensitive."""
        from logger import sanitize_dict
        data = {'PASSWORD': 'secret', 'ApiKey': 'key123'}
        sanitized = sanitize_dict(data)
        assert sanitized['PASSWORD'] == '[REDACTED]'
        assert sanitized['ApiKey'] == '[REDACTED]'

    def test_sanitize_nested_dict(self):
        """Test that nested dictionaries are recursively sanitized."""
        from logger import sanitize_dict
        data = {
            'user': {
                'name': 'john',
                'password': 'secret123'
            }
        }
        sanitized = sanitize_dict(data)
        assert sanitized['user']['password'] == '[REDACTED]'
        assert sanitized['user']['name'] == 'john'

    def test_sanitize_custom_keys(self):
        """Test sanitization with custom sensitive keys."""
        from logger import sanitize_dict
        data = {'public_id': '123', 'private_id': '456'}
        sanitized = sanitize_dict(data, sensitive_keys={'private_id'})
        assert sanitized['private_id'] == '[REDACTED]'
        assert sanitized['public_id'] == '123'

    def test_sanitize_multiple_sensitive_keys(self):
        """Test that multiple sensitive keys are redacted."""
        from logger import sanitize_dict
        data = {
            'username': 'john',
            'password': 'secret',
            'token': 'abc123',
            'secret': 'xyz789'
        }
        sanitized = sanitize_dict(data)
        assert sanitized['password'] == '[REDACTED]'
        assert sanitized['token'] == '[REDACTED]'
        assert sanitized['secret'] == '[REDACTED]'
        assert sanitized['username'] == 'john'


class TestMaskCreditCard:
    """Test the mask_credit_card function."""

    def test_mask_16_digit_card(self):
        """Test masking a 16-digit credit card."""
        from logger import mask_credit_card
        result = mask_credit_card('4532123456789010')
        assert result == '****9010'

    def test_mask_card_with_spaces(self):
        """Test masking card number with spaces."""
        from logger import mask_credit_card
        result = mask_credit_card('4532 1234 5678 9010')
        assert result == '****9010'

    def test_mask_card_with_dashes(self):
        """Test masking card number with dashes."""
        from logger import mask_credit_card
        result = mask_credit_card('4532-1234-5678-9010')
        assert result == '****9010'

    def test_mask_short_card(self):
        """Test masking invalid short card number."""
        from logger import mask_credit_card
        result = mask_credit_card('123')
        assert result == '[INVALID-CC]'


class TestMaskEmail:
    """Test the mask_email function."""

    def test_mask_normal_email(self):
        """Test masking a normal email address."""
        from logger import mask_email
        result = mask_email('john.doe@example.com')
        assert result == 'j***@example.com'

    def test_mask_short_email(self):
        """Test masking email with single character before @."""
        from logger import mask_email
        result = mask_email('a@example.com')
        assert result == '*@example.com'

    def test_mask_invalid_email(self):
        """Test masking invalid email without @."""
        from logger import mask_email
        result = mask_email('notanemail')
        assert result == '[INVALID-EMAIL]'

    def test_mask_preserves_domain(self):
        """Test that domain is preserved in masking."""
        from logger import mask_email
        result = mask_email('alice@company.org')
        assert '@company.org' in result
        assert 'alice' not in result


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_secure_logger_with_dict(self, caplog):
        """Test logging sanitized dictionaries with secure logger."""
        from logger import get_secure_logger, sanitize_dict
        logger = get_secure_logger('test_integration_dict')
        
        data = {
            'user_id': '12345',
            'password': 'secret123',
            'api_key': 'sk_live_abc'
        }
        
        sanitized = sanitize_dict(data)
        
        with caplog.at_level(logging.INFO, logger='test_integration_dict'):
            logger.info("User data: %s", sanitized)
        
        # Check that sensitive data is redacted
        assert 'secret123' not in caplog.text
        assert 'sk_live_abc' not in caplog.text
        assert '[REDACTED]' in caplog.text
        assert '12345' in caplog.text

    def test_real_world_login_scenario(self, caplog):
        """Test a realistic login scenario with multiple sensitive fields."""
        from logger import get_secure_logger, sanitize_dict, mask_email, mask_credit_card
        logger = get_secure_logger('test_integration_login')
        
        # Simulate user data from a login attempt
        user_data = {
            'username': 'john_doe',
            'email': 'john.doe@example.com',
            'password': 'super_secret_password',
            'api_key': 'sk_live_abc123xyz',
            'credit_card': '4532-1234-5678-9010',
            'user_id': '42'
        }
        
        # Mask email and credit card before sanitizing
        # (so we preserve partial information instead of full redaction)
        user_data['email'] = mask_email(user_data['email'])
        user_data['credit_card'] = mask_credit_card(user_data['credit_card'])
        
        # Sanitize the dict (redacts password, api_key, etc.)
        # Don't redact credit_card since we already masked it
        sensitive = {'password', 'pwd', 'passwd', 'api_key', 'apikey', 
                    'api-key', 'secret', 'token', 'auth', 'ssn', 'social_security'}
        safe_data = sanitize_dict(user_data, sensitive_keys=sensitive)
        
        with caplog.at_level(logging.INFO, logger='test_integration_login'):
            logger.info("Login attempt: %s", safe_data)
        
        # Verify sensitive data is protected
        assert 'super_secret_password' not in caplog.text
        assert 'sk_live_abc123xyz' not in caplog.text
        assert 'john.doe@example.com' not in caplog.text
        assert '4532-1234-5678-9010' not in caplog.text
        
        # Verify safe data is present
        assert 'john_doe' in caplog.text
        assert 'j***@example.com' in caplog.text
        assert '****9010' in caplog.text
        assert '[REDACTED]' in caplog.text
        assert '42' in caplog.text
