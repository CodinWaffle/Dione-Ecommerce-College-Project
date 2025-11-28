#!/usr/bin/env python3
"""
Simple check for variant data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct
import json

def check_variants():
    app = create_app()
    
    with app.app_context():
        # Get first product
        product = SellerProduct.query.first()
        if product:
            print(f"Product: {product.name}")
            print(f"Variants: {product.variants}")
            print(f"Type: {type(product.variants)}")
            
            if not product.variants:
                print("No variants found - creating sample data...")
                sample_variants = [
                    {
                        "color": "Red",
                        "colorHex": "#FF0000",
                        "sizeStocks": [
                            {"size": "S", "stock": 10},
                            {"size": "M", "stock": 15}
                        ]
                    }
                ]
                product.variants = json.dumps(sample_variants)
                db.session.commit()
                print("Sample variants created")
        else:
            print("No products found")

if __name__ == "__main__":
    check_variants()