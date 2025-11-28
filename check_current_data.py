#!/usr/bin/env python
"""Simple database verification"""

import mysql.connector
from mysql.connector import Error
import json

def check_database():
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            database='dione_data',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Get all products with their full data
            query = """
            SELECT id, seller_id, base_sku, draft_data, is_draft, created_at
            FROM seller_product_management
            ORDER BY created_at DESC
            LIMIT 10
            """
            cursor.execute(query)
            products = cursor.fetchall()
            
            print("=== CURRENT DATABASE STATE ===")
            print(f"Found {len(products)} products in database:\n")
            
            for product in products:
                print(f"Product ID: {product['id']}")
                print(f"Seller ID: {product['seller_id']}")
                print(f"Base SKU: {product['base_sku']}")
                print(f"Is Draft: {product['is_draft']}")
                print(f"Created: {product['created_at']}")
                
                # Parse and display draft_data
                if product['draft_data']:
                    try:
                        draft_data = json.loads(product['draft_data'])
                        print(f"Draft Data:")
                        print(f"  - Product Name: {draft_data.get('productName', 'N/A')}")
                        print(f"  - Category: {draft_data.get('category', 'N/A')}")
                        print(f"  - Price: {draft_data.get('price', 'N/A')}")
                        print(f"  - Variants: {len(draft_data.get('variants', []))}")
                        
                        # Show variant details
                        variants = draft_data.get('variants', [])
                        total_stock = 0
                        if variants:
                            print(f"  Variant Details:")
                            for i, variant in enumerate(variants):
                                stock = variant.get('stock', 0)
                                total_stock += stock
                                print(f"    {i+1}. Color: {variant.get('color', 'N/A')}, Size: {variant.get('size', 'N/A')}, Stock: {stock}")
                        print(f"  - Total Stock: {total_stock}")
                        
                    except json.JSONDecodeError as e:
                        print(f"  - Draft Data: [Invalid JSON: {e}]")
                else:
                    print("  - Draft Data: None")
                    
                print("  " + "="*50)
                
    except Error as e:
        print(f"Database error: {e}")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_database()