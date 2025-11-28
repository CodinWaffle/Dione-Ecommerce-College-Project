import requests

# Get the actual HTML being served
response = requests.get('http://localhost:5000/seller/add_product_stocks')
print(f"Status: {response.status_code}")
print("First 1000 characters of HTML:")
print("="*50)
print(response.text[:1000])
print("="*50)
print("\nLast 1000 characters of HTML:")
print("="*50)
print(response.text[-1000:])
print("="*50)

# Save full HTML to file for inspection
with open('rendered_html.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Full HTML saved to 'rendered_html.html'")

# Check if this looks like the right template
if "Inventory Management" in response.text:
    print("✅ Contains 'Inventory Management' - likely correct page")
else:
    print("❌ Missing 'Inventory Management' - wrong page?")