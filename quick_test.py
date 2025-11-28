import requests

print('🔍 Simple HTML Content Check...')

try:
    response = requests.get('http://localhost:5000/seller/add_product_stocks', timeout=10)
    html_content = response.text
    
    print(f'📊 Response Status: {response.status_code}')
    print(f'📄 HTML Length: {len(html_content)} characters')
    
    # Check for key elements
    checks = [
        ('Add Variant Button ID', 'id="addVariantBtn"'),
        ('Photo Upload Box Class', 'photo-upload-box'),
        ('Variant Table Body', 'id="variantTableBody"'),
        ('Variant Manager Script', 'Variant table manager loading'),
        ('Photo Upload Script', 'GLOBAL Photo Upload Handler'),
        ('Setup Photo Function', 'window.setupPhotoUpload'),
        ('Add Variant Function', 'addVariantRow'),
        ('File Input in Photo Box', 'type="file"'),
        ('Remove Variant Function', 'removeVariantRow'),
    ]
    
    print('\\n🔍 Element Check Results:')
    all_found = True
    
    for name, search_text in checks:
        found = search_text in html_content
        status = '✅' if found else '❌'
        print(f'   {status} {name}: {"Found" if found else "NOT FOUND"}')
        if not found:
            all_found = False
    
    print('\\n🔧 JavaScript Console Messages Expected:')
    if 'Variant table manager loading' in html_content:
        print('   ✅ Should see: "🔧 Variant table manager loading..."')
    if 'GLOBAL Photo Upload' in html_content:
        print('   ✅ Should see: "🔧 INITIALIZING GLOBAL PHOTO UPLOAD..."')
    
    print('\\n🎯 FINAL VERDICT:')
    if all_found:
        print('   🟢 ALL FUNCTIONALITY SHOULD BE WORKING!')
        print('   📋 Add Variant Button: Ready to add new rows')
        print('   📸 Photo Upload: Ready for image uploads')
    else:
        print('   🔴 SOME ELEMENTS MISSING - Functionality may be broken')
    
    print('\\n💡 Manual Test Instructions:')
    print('   1. Open browser to: http://localhost:5000/seller/add_product_stocks')
    print('   2. Click the "Add Variant" button - should add a new table row')
    print('   3. Click any photo upload box - should open file picker')
    print('   4. Check browser console (F12) for any JavaScript errors')
    
except requests.exceptions.RequestException as e:
    print(f'❌ Could not connect to server: {e}')
    print('   Make sure Flask server is running on localhost:5000')
except Exception as e:
    print(f'❌ Test failed: {e}')