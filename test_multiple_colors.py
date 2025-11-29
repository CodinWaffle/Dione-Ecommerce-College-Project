#!/usr/bin/env python3
import requests

colors = ['Digital Lavender', 'Nordic Blue', 'Black', 'Cool White']
print('Testing API for product 38 with multiple colors:')

for color in colors:
    try:
        response = requests.get(f'http://localhost:5000/api/product/38/sizes/{color}')
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('sizes'):
                sizes = data['sizes']
                print(f'  🎨 {color}: {len(sizes)} sizes found')
                for size, info in sizes.items():
                    stock = info.get('stock', 0)
                    print(f'    {size}: {stock} units')
            else:
                print(f'  ❌ {color}: No sizes returned')
        else:
            print(f'  ❌ {color}: API error {response.status_code}')
    except Exception as e:
        print(f'  ⚠️  {color}: Server not running')
        break