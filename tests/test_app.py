import pytest
from app import create_app, db
from app import Pastry, Customer, Order, OrderItem

@pytest.fixture
def app():
    """Create and configure a new app instance for each test"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

def test_index_page(client):
    """Test the home page returns 200 OK"""
    response = client.get('/')
    assert response.status_code == 200

def test_browse_page(client):
    """Test the browse page returns 200 OK"""
    response = client.get('/browse')
    assert response.status_code == 200

def test_pastry_creation(app):
    """Test pastry creation"""
    with app.app_context():
        pastry = Pastry(name='Croissant', price=2.99)
        db.session.add(pastry)
        db.session.commit()
        
        assert Pastry.query.count() == 1
        assert Pastry.query.first().name == 'Croissant'

def test_api_pastries(client):
    """Test the API endpoint returns JSON"""
    response = client.get('/api/pastries')
    assert response.status_code == 200
    assert response.is_json

def test_cart_empty(client):
    """Test empty cart page"""
    response = client.get('/cart')
    assert response.status_code == 200

def test_checkout_empty_cart(client):
    """Test checkout with empty cart redirects"""
    response = client.get('/checkout')
    # Should redirect to browse page when cart is empty
    assert response.status_code == 302