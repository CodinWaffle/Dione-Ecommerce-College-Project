#!/usr/bin/env python3
"""
Test script to verify color selection is working properly
"""

def test_javascript_functions():
    """Test that the JavaScript functions are properly defined"""
    
    print("🔍 Testing JavaScript Function Definitions...")
    
    try:
        with open('project/static/js/buyer_scripts/product_detail.js', 'r') as f:
            js_content = f.read()
            
        issues = []
        
        # Check for single selectColor function
        selectColor_count = js_content.count('function selectColor(')
        if selectColor_count == 1:
            print("✅ Single selectColor function found")
        else:
            issues.append(f"❌ Found {selectColor_count} selectColor functions (should be 1)")
            
        # Check that selectColor calls updateSizeAvailability
        if 'updateSizeAvailability()' in js_content:
            print("✅ selectColor calls updateSizeAvailability()")
        else:
            issues.append("❌ selectColor doesn't call updateSizeAvailability()")
            
        # Check that updateSizeOptions function is removed
        updateSizeOptions_count = js_content.count('function updateSizeOptions(')
        if updateSizeOptions_count == 0:
            print("✅ updateSizeOptions function removed")
        else:
            issues.append(f"❌ Found {updateSizeOptions_count} updateSizeOptions functions (should be 0)")
            
        # Check that global updateSizeOptions reference is removed
        if 'window.updateSizeOptions' not in js_content:
            print("✅ Global updateSizeOptions reference removed")
        else:
            issues.append("❌ Global updateSizeOptions reference still present")
            
        # Check for API call in updateSizeAvailability
        if '/api/product/${productId}/sizes/${encodeURIComponent(selectedColor)}' in js_content:
            print("✅ API call present in updateSizeAvailability")
        else:
            issues.append("❌ API call missing in updateSizeAvailability")
            
        if issues:
            print(f"\n❌ Issues found:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print(f"\n✅ All JavaScript functions are properly configured!")
            return True
            
    except FileNotFoundError:
        print("❌ product_detail.js file not found")
        return False

def test_template_onclick():
    """Test that the template has proper onclick handlers"""
    
    print(f"\n🔍 Testing Template onclick Handlers...")
    
    try:
        with open('project/templates/main/product_detail.html', 'r') as f:
            template_content = f.read()
            
        issues = []
        
        # Check for onclick="selectColor(this)"
        if 'onclick="selectColor(this)"' in template_content:
            print("✅ Color buttons have onclick handlers")
        else:
            issues.append("❌ Color buttons missing onclick handlers")
            
        # Check for sizeOptions container
        if 'id="sizeOptions"' in template_content:
            print("✅ sizeOptions container present")
        else:
            issues.append("❌ sizeOptions container missing")
            
        # Check that conflicting inline scripts are removed
        if 'window.selectColor = function' not in template_content:
            print("✅ No conflicting inline selectColor function")
        else:
            issues.append("❌ Conflicting inline selectColor function still present")
            
        if issues:
            print(f"\n❌ Template issues found:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print(f"\n✅ Template is properly configured!")
            return True
            
    except FileNotFoundError:
        print("❌ product_detail.html template not found")
        return False

if __name__ == "__main__":
    print("🚀 Testing Color Selection Fix\n")
    
    js_ok = test_javascript_functions()
    template_ok = test_template_onclick()
    
    print(f"\n" + "="*50)
    print(f"📋 FINAL RESULTS:")
    print(f"   JavaScript Functions: {'✅ PASS' if js_ok else '❌ FAIL'}")
    print(f"   Template Configuration: {'✅ PASS' if template_ok else '❌ FAIL'}")
    
    if js_ok and template_ok:
        print(f"\n🎉 SUCCESS! Color selection should now work properly.")
        print(f"   - Colors should be clickable (not just hoverable)")
        print(f"   - Sizes should appear when colors are selected")
        print(f"   - Each color should show different sizes from the database")
    else:
        print(f"\n⚠️  Some issues remain. Check the details above.")
    
    print(f"\n💡 To test manually:")
    print(f"   1. Start the Flask server")
    print(f"   2. Go to any product detail page")
    print(f"   3. Click on different colors (not just hover)")
    print(f"   4. Verify that sizes appear and are different for each color")