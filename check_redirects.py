import requests

print("🔍 Checking for redirects...")

# Test with redirect following disabled
response = requests.get('http://localhost:5000/seller/add_product_stocks', allow_redirects=False)
print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

if response.status_code in [301, 302, 303, 307, 308]:
    print(f"🔄 REDIRECT detected to: {response.headers.get('Location', 'Unknown')}")
else:
    print("📄 No redirect - response is final")
    
# Also test following redirects to see where we end up
response_with_redirects = requests.get('http://localhost:5000/seller/add_product_stocks', allow_redirects=True)
print(f"\nFinal URL after redirects: {response_with_redirects.url}")
print(f"Final status: {response_with_redirects.status_code}")

# Check if we ended up on login page or main site
if 'login' in response_with_redirects.url.lower():
    print("🔐 Ended up on login page - authentication required")
elif 'profile' in response_with_redirects.url.lower():
    print("👤 Ended up on profile page - seller role required")  
else:
    print(f"🎯 Ended up on: {response_with_redirects.url}")