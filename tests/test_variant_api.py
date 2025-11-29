"""
Unit tests for the product variant API endpoints and functionality.
Tests the color/size selection workflow and stock validation.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from flask import session

from project import create_app, db
from project.models import SellerProduct, ProductVariant, VariantSize, User


class TestVariantAPI:
    """Test cases for the variant selection API."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def sample_product(self, app):
        """Create a sample product with variants."""
        with app.app_context():
            # Create seller user
            seller = User(
                email='seller@test.com',
                role='seller',
                is_approved=True
            )
            db.session.add(seller)
            db.session.commit()

            # Create product with variant JSON structure
            variants_data = [
                {
                    "color": "Black",
                    "colorHex": "#000000",
                    "sizeStocks": [
                        {"size": "XS", "stock": 10},
                        {"size": "S", "stock": 15},
                        {"size": "M", "stock": 20},
                        {"size": "L", "stock": 5},
                        {"size": "XL", "stock": 0}
                    ]
                },
                {
                    "color": "Red",
                    "colorHex": "#ff0000",
                    "sizeStocks": [
                        {"size": "S", "stock": 8},
                        {"size": "M", "stock": 12},
                        {"size": "L", "stock": 3}
                    ]
                }
            ]

            product = SellerProduct(
                seller_id=seller.id,
                name="Test Product",
                price=99.99,
                variants=variants_data,
                status='active'
            )
            db.session.add(product)
            db.session.commit()

            return product

    @pytest.fixture
    def sample_product_variant_model(self, app):
        """Create a sample product using the ProductVariant model."""
        with app.app_context():
            # Create seller user
            seller = User(
                email='seller2@test.com',
                role='seller',
                is_approved=True
            )
            db.session.add(seller)
            db.session.commit()

            # Create product
            product = SellerProduct(
                seller_id=seller.id,
                name="Test Variant Product",
                price=79.99,
                status='active'
            )
            db.session.add(product)
            db.session.commit()

            # Create color variant
            variant = ProductVariant(
                product_id=product.id,
                variant_name="Blue",
                variant_sku="TEST-BLUE"
            )
            db.session.add(variant)
            db.session.commit()

            # Create sizes for the variant
            sizes = [
                VariantSize(variant_id=variant.id, size_label="XS", stock_quantity=5, sku="TEST-BLUE-XS"),
                VariantSize(variant_id=variant.id, size_label="S", stock_quantity=10, sku="TEST-BLUE-S"),
                VariantSize(variant_id=variant.id, size_label="M", stock_quantity=0, sku="TEST-BLUE-M"),
                VariantSize(variant_id=variant.id, size_label="L", stock_quantity=7, sku="TEST-BLUE-L")
            ]
            
            for size in sizes:
                db.session.add(size)
            db.session.commit()

            return product

    def test_get_sizes_for_color_json_structure(self, client, sample_product):
        """Test getting sizes for a color using JSON variant structure."""
        response = client.get(f'/api/products/{sample_product.id}/colors/Black/sizes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['color'] == 'Black'
        assert len(data['sizes']) == 5
        
        # Check size data structure
        for size_info in data['sizes']:
            assert 'size' in size_info
            assert 'stock' in size_info
            assert 'available' in size_info
            assert 'low_stock' in size_info

        # Verify specific sizes
        sizes_dict = {s['size']: s for s in data['sizes']}
        
        assert sizes_dict['XS']['stock'] == 10
        assert sizes_dict['XS']['available'] is True
        assert sizes_dict['XS']['low_stock'] is False
        
        assert sizes_dict['L']['stock'] == 5
        assert sizes_dict['L']['available'] is True
        assert sizes_dict['L']['low_stock'] is True  # 5 <= 3 is False, but 5 > 0 and 5 <= 5, so depends on threshold
        
        assert sizes_dict['XL']['stock'] == 0
        assert sizes_dict['XL']['available'] is False

    def test_get_sizes_for_color_variant_model(self, client, sample_product_variant_model):
        """Test getting sizes using ProductVariant model."""
        response = client.get(f'/api/products/{sample_product_variant_model.id}/colors/Blue/sizes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['color'] == 'Blue'
        assert 'variant_id' in data
        assert len(data['sizes']) == 4
        
        # Verify SKUs are included
        sizes_dict = {s['size']: s for s in data['sizes']}
        assert sizes_dict['XS']['sku'] == 'TEST-BLUE-XS'
        assert sizes_dict['M']['available'] is False  # 0 stock

    def test_get_sizes_nonexistent_color(self, client, sample_product):
        """Test getting sizes for a color that doesn't exist."""
        response = client.get(f'/api/products/{sample_product.id}/colors/Purple/sizes')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'Color variant not found' in data['error']

    def test_get_sizes_nonexistent_product(self, client):
        """Test getting sizes for a product that doesn't exist."""
        response = client.get('/api/products/99999/colors/Black/sizes')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['success'] is False

    def test_add_to_cart_with_stock_validation(self, client, sample_product):
        """Test add to cart with proper stock validation."""
        # Test successful add to cart
        cart_data = {
            'product_id': sample_product.id,
            'color': 'Black',
            'size': 'S',
            'quantity': 2,
            'color_hex': '#000000',
            'image_url': '/static/test.jpg'
        }
        
        response = client.post('/add-to-cart',
                             data=json.dumps(cart_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'remaining_stock' in data
        assert data['remaining_stock'] == 13  # 15 - 2

    def test_add_to_cart_out_of_stock(self, client, sample_product):
        """Test add to cart when item is out of stock."""
        cart_data = {
            'product_id': sample_product.id,
            'color': 'Black',
            'size': 'XL',  # This size has 0 stock
            'quantity': 1,
            'color_hex': '#000000',
            'image_url': '/static/test.jpg'
        }
        
        response = client.post('/add-to-cart',
                             data=json.dumps(cart_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        
        assert 'out of stock' in data['message'].lower()

    def test_add_to_cart_exceeds_stock(self, client, sample_product):
        """Test add to cart when quantity exceeds available stock."""
        cart_data = {
            'product_id': sample_product.id,
            'color': 'Black',
            'size': 'L',  # This size has 5 stock
            'quantity': 10,  # Requesting more than available
            'color_hex': '#000000',
            'image_url': '/static/test.jpg'
        }
        
        response = client.post('/add-to-cart',
                             data=json.dumps(cart_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        
        assert 'insufficient stock' in data['message'].lower()
        assert data['available_stock'] == 5

    def test_add_to_cart_missing_fields(self, client, sample_product):
        """Test add to cart with missing required fields."""
        cart_data = {
            'product_id': sample_product.id,
            'color': 'Black',
            # Missing size
            'quantity': 1
        }
        
        response = client.post('/add-to-cart',
                             data=json.dumps(cart_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert 'missing required fields' in data['error'].lower()

    def test_add_to_cart_cart_accumulation(self, client, sample_product):
        """Test that cart accumulates items correctly and respects stock limits."""
        with client.session_transaction() as sess:
            # Add some items to session cart first
            sess['cart_items'] = [{
                'product_id': sample_product.id,
                'color': 'Black',
                'size': 'L',
                'quantity': 3  # Already have 3 in cart
            }]
        
        # Try to add 3 more (total would be 6, but only 5 available)
        cart_data = {
            'product_id': sample_product.id,
            'color': 'Black',
            'size': 'L',
            'quantity': 3,
            'color_hex': '#000000',
            'image_url': '/static/test.jpg'
        }
        
        response = client.post('/add-to-cart',
                             data=json.dumps(cart_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        
        assert 'exceeds available stock' in data['message'].lower()
        assert data['available_to_add'] == 2  # 5 - 3 = 2 more can be added

    def test_api_response_format_consistency(self, client, sample_product):
        """Test that API responses have consistent format."""
        response = client.get(f'/api/products/{sample_product.id}/colors/Red/sizes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields
        required_fields = ['success', 'color', 'sizes', 'total_stock']
        for field in required_fields:
            assert field in data
        
        # Check size object structure
        for size_info in data['sizes']:
            size_fields = ['size', 'stock', 'available', 'low_stock']
            for field in size_fields:
                assert field in size_info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])