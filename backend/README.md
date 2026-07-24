Developer notes

This backend uses bcrypt for password hashing via `passlib[bcrypt]`.

If you encounter errors like "password cannot be longer than 72 bytes" or issues with the `bcrypt` backend when running locally, ensure a compatible `bcrypt` wheel is installed.

Recommended steps (Windows / Linux / macOS):

1. Activate your virtual environment.
2. Install the pinned bcrypt version and other requirements:

```bash
pip install bcrypt==4.0.1
pip install -r requirements.txt
```

3. Verify bcrypt import and version in Python:

```python
import bcrypt
print(bcrypt.__version__)
```

If `bcrypt` fails to import or has unexpected attributes, reinstall or try another compatible wheel. For local development only, the project previously included a runtime fallback to `pbkdf2_sha256` to avoid blocking registration when `bcrypt` is unavailable — that fallback has been removed to keep hashing consistent with production. If you need a quick local workaround, reinstall `bcrypt` or ask the maintainer to reintroduce the fallback.
