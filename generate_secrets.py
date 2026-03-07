"""
Generate secure secrets for Render deployment
Run: python generate_secrets.py
"""

import secrets
import base64

print("=" * 60)
print("SECURE SECRETS FOR RENDER DEPLOYMENT")
print("=" * 60)
print("\n📋 Copy these values to Render Dashboard:\n")

# JWT Secret (64 characters)
jwt_secret = secrets.token_urlsafe(48)
print(f"JWT_SECRET={jwt_secret}")

# JWT Refresh Secret (64 characters)
jwt_refresh_secret = secrets.token_urlsafe(48)
print(f"JWT_REFRESH_SECRET={jwt_refresh_secret}")

# Encryption Key (32 bytes base64)
encryption_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
print(f"ENCRYPTION_KEY={encryption_key}")

print("\n" + "=" * 60)
print("⚠️  SAVE THESE VALUES - They cannot be recovered!")
print("=" * 60)
print("\n📝 Additional Actions Required:")
print("  1. Create AWS S3 bucket at: https://console.aws.amazon.com/s3")
print("  2. Generate GitHub token at: https://github.com/settings/tokens")
print("  3. Get SendGrid key at: https://app.sendgrid.com/settings/api_keys")
print("  4. Deploy smart contract (see blockchain/README.md)")
