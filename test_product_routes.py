"""
Test script to verify product routes are properly configured
"""
from project import create_app

app = create_app('development')

with app.app_context():
    # Get all registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        if 'seller' in rule.rule and 'product' in rule.rule:
            routes.append({
                'endpoint': rule.endpoint,
                'methods': ','.join(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': rule.rule
            })
    
    print("=" * 60)
    print("SELLER PRODUCT ROUTES")
    print("=" * 60)
    
    for route in sorted(routes, key=lambda x: x['path']):
        print(f"\n{route['path']}")
        print(f"  Endpoint: {route['endpoint']}")
        print(f"  Methods: {route['methods']}")
    
    print("\n" + "=" * 60)
    print(f"Total product routes found: {len(routes)}")
    print("=" * 60)
