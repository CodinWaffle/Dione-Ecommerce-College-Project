import requests
from bs4 import BeautifulSoup

print('🔍 Detailed HTML Analysis...')

try:
    response = requests.get('http://localhost:5000/seller/add_product_stocks')
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f'📄 Page title: {soup.title.text if soup.title else "No title"}')
    print(f'📊 Total HTML length: {len(response.text)} characters')
    
    # Check for specific elements
    add_btn = soup.find('button', {'id': 'addVariantBtn'})
    print(f'🔘 Add Variant Button: {"Found" if add_btn else "NOT FOUND"}')
    
    photo_boxes = soup.find_all(class_='photo-upload-box')
    print(f'📸 Photo upload boxes: {len(photo_boxes)} found')
    
    variant_table = soup.find('tbody', {'id': 'variantTableBody'})
    print(f'📋 Variant table body: {"Found" if variant_table else "NOT FOUND"}')
    
    # Check for scripts
    scripts = soup.find_all('script')
    script_with_variant = any('Variant table manager' in str(script) for script in scripts)
    script_with_photo = any('GLOBAL Photo Upload' in str(script) for script in scripts)
    
    print(f'📜 Script with variant manager: {script_with_variant}')
    print(f'📜 Script with photo upload: {script_with_photo}')
    print(f'📜 Total scripts found: {len(scripts)}')
    
    # Check for CSS
    css_links = soup.find_all('link', {'rel': 'stylesheet'})
    print(f'🎨 CSS files linked: {len(css_links)}')
    
    # Look for any obvious errors in HTML
    if 'error' in response.text.lower() or 'exception' in response.text.lower():
        print('⚠️ Possible errors detected in HTML')
    else:
        print('✅ No obvious errors in HTML')
        
    # Test the actual functionality by checking console logs
    print('\n🔧 Testing Core Elements:')
    
    if add_btn:
        print(f'   ✅ Add Variant Button Text: "{add_btn.get_text().strip()}"')
        print(f'   ✅ Button Classes: {add_btn.get("class", [])}')
    
    if photo_boxes:
        print(f'   📸 First photo box classes: {photo_boxes[0].get("class", [])}')
        
    print('\n🎯 VERDICT:')
    if add_btn and variant_table and len(scripts) > 0:
        print('✅ ALL KEY ELEMENTS FOUND - Functionality should work!')
    else:
        print('❌ MISSING KEY ELEMENTS - Functionality may not work')
        
except Exception as e:
    print(f'❌ Analysis failed: {e}')