import pytest
from pydantic import BaseModel, EmailStr, ValidationError

# Define a Pydantic model that uses EmailStr for validation
class User(BaseModel):
    email: EmailStr

# Test cases for valid emails, including various formats
valid_emails = [
    "simple@example.com",
    "very.common@example.com",
    "disposable.style.email.with+symbol@example.com",
    "other.email-with-hyphen@example.com",
    "fully-qualified-domain@example.com",
    "user.name+tag+sorting@example.com",  # Plus-tagging
    "x@example.com",  # One-letter local part
    '"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@strange.example.com',
    "example-indeed@strange-example.com",
    "admin@mailserver1",
    "test/user@jyotiflow.ai", # Test with slash
    "customer/department=shipping@example.com", # Test with slash and equals
    "संस्कृत@उदाहरण.कॉम",  # Unicode local part (Sanskrit)
    "परीक्षण@domain.com", # Unicode local part 2 (Hindi)
    "test@उदाहरण.भारत",  # Unicode domain part (Hindi)
    "ผู้ใช้@โดเมน.ไทย",  # Thai characters
    "παράδειγμα@δοκιμή.gr",  # Greek characters
]

# Test cases for invalid emails
invalid_emails = [
    "Abc.example.com",  # No @ symbol
    "A@b@c@example.com",  # Multiple @ symbols
    'a"b(c)d,e:f;g<h>i[j\\k]l@example.com', # Special characters not in quotes
    "just\"not\"right@example.com",
    "this is\"not\\allowed@example.com",
    "this\\ still\\\"not\\\\allowed@example.com",
    "1234567890123456789012345678901234567890123456789012345678901234+x@example.com", # Local part too long
    "test@.com", # Domain starts with a dot
    "test@com.", # Domain ends with a dot
    ".test@com", # Local part starts with a dot
]

@pytest.mark.parametrize("email", valid_emails)
def test_valid_emails_with_pydantic(email):
    """
    Tests that various valid email formats, including plus-tagging and Unicode,
    pass Pydantic's EmailStr validation. This is a round-trip test.
    """
    try:
        user = User(email=email)
        # Check that the parsed email is the same as the input
        assert user.email == email
    except ValidationError as e:
        pytest.fail(f"Email '{email}' was considered invalid but should be valid. Error: {e}")

@pytest.mark.parametrize("email", invalid_emails)
def test_invalid_emails_with_pydantic(email):
    """
    Tests that invalid email formats are correctly rejected by Pydantic's EmailStr.
    """
    with pytest.raises(ValidationError):
        User(email=email)

def test_pydantic_plus_tagging_specific():
    """
    Specifically tests the plus-tagging feature, which is critical for many systems.
    """
    email = "user.name+important-tag@example.com"
    user = User(email=email)
    assert user.email == email

def test_pydantic_unicode_specific():
    """
    Specifically tests Unicode characters in both local and domain parts.
    """
    email = "उपयोगकर्ता+परीक्षण@उदाहरण.कॉम" # Hindi for "user+test@example.com"
    user = User(email=email)
    assert user.email == email
