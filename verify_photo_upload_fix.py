#!/usr/bin/env python3
"""
Verify that the photo upload fix is properly implemented
"""

import os

def verify_photo_upload_fix():
    print("🔍 Verifying Photo Upload Fix")
    print("=" * 50)
    
    # Check if template has the simple fix
    template_path = "project/templates/seller/add_product_stocks.html"
    
    if not os.path.exists(template_path):
        print("❌ Template file not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for key components
    checks = {
        "Force photo upload fix": "Force photo upload fix" in template_content,
        "handlePhotoUpload function": "function handlePhotoUpload" in template_content,
        "initPhotoBoxes function": "function initPhotoBoxes" in template_content,
        "onclick handler": "photoBox.onclick" in template_content,
        "onchange handler": "input.onchange" in template_content,
        "File validation": "file.type.startsWith('image/')" in template_content,
        "Size validation": "file.size > 5 * 1024 * 1024" in template_content,
        "Preview creation": "createElement('img')" in template_content,
        "Remove button": "remove-photo" in template_content,
        "Global function": "window.forceInitPhotoBoxes" in template_content,
        "Multiple initialization": "setTimeout(initPhotoBoxes" in template_content
    }
    
    print("📋 Template Check Results:")
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        if not result:
            all_passed = False
    
    # Check for duplicate/old code
    print("\n🧹 Checking for old/duplicate code:")
    old_code_patterns = [
        "setupVariantPhoto",
        "addEventListener('click'",
        "dataset.immediateSetup",
        "dataset.hasHandler"
    ]
    
    old_code_found = False
    for pattern in old_code_patterns:
        if pattern in template_content:
            print(f"  ⚠️  Found old code pattern: {pattern}")
            old_code_found = True
    
    if not old_code_found:
        print("  ✅ No old/duplicate code found")
    
    # Check script structure
    print("\n📜 Script Structure Check:")
    script_count = template_content.count("<script>")
    script_close_count = template_content.count("</script>")
    
    print(f"  Script tags: {script_count} opening, {script_close_count} closing")
    
    if script_count == script_close_count:
        print("  ✅ Script tags are balanced")
    else:
        print("  ❌ Script tags are not balanced")
        all_passed = False
    
    # Check for the specific photo upload box HTML
    print("\n🏗️  HTML Structure Check:")
    html_checks = {
        "Photo upload box": 'class="photo-upload-box grey"' in template_content,
        "File input": 'type="file" accept="image/*"' in template_content,
        "Upload content": 'class="photo-upload-content"' in template_content,
        "Camera icon": 'ri-image-add-line' in template_content
    }
    
    for check, result in html_checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Photo Upload Fix Verification: PASSED")
        print("\n📋 What to do next:")
        print("1. Open your browser and go to /seller/add_product_stocks")
        print("2. Click on any gray photo upload box")
        print("3. Select an image file")
        print("4. Verify the preview appears")
        print("5. Test the remove button (×)")
        print("\n🧪 For standalone testing:")
        print("   Open test_photo_upload_simple.html in your browser")
        
        return True
    else:
        print("❌ Photo Upload Fix Verification: FAILED")
        print("\n🔧 Issues found that need to be fixed")
        return False

if __name__ == "__main__":
    verify_photo_upload_fix()