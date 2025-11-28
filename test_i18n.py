from datetime import datetime
from app.utils.i18n import setup_i18n, format_date, translate

# Initialiser i18n
setup_i18n()

# Date de test
test_date = datetime(2025, 11, 23, 15, 30, 0)

print("=== TEST TRADUCTION ===\n")

# Test formats de dates
print("1. Formats de dates:")
print(f"   EN: {format_date(test_date, 'en')}")
print(f"   FR: {format_date(test_date, 'fr')}")

# Test messages
print("\n2. Messages traduits:")
messages = ["user_created", "invalid_email", "not_found"]

for msg in messages:
    print(f"\n   {msg}:")
    print(f"      EN: {translate(msg, 'en')}")
    print(f"      FR: {translate(msg, 'fr')}")

print("\n=== FIN TEST ===")
