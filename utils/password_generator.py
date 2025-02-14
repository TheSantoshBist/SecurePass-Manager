import secrets
import string

class PasswordGenerator:
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate(self, length: int = 16,
                use_uppercase: bool = True,
                use_digits: bool = True,
                use_symbols: bool = True) -> str:
        # Start with lowercase letters
        characters = self.lowercase

        if use_uppercase:
            characters += self.uppercase
        if use_digits:
            characters += self.digits
        if use_symbols:
            characters += self.symbols

        # Ensure at least one character from each selected type
        password = [
            secrets.choice(self.lowercase),
            secrets.choice(self.uppercase) if use_uppercase else '',
            secrets.choice(self.digits) if use_digits else '',
            secrets.choice(self.symbols) if use_symbols else ''
        ]

        # Fill the rest randomly
        remaining_length = length - len(''.join(password))
        password.extend(secrets.choice(characters) for _ in range(remaining_length))

        # Shuffle the password
        password_list = list(''.join(password))
        secrets.SystemRandom().shuffle(password_list)

        return ''.join(password_list)