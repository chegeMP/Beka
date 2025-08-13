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

def test_pastry_creation(app):
    """Test pastry creation"""
    with app.app_context():
        pastry = Pastry(name='Croissant', price=2.99)
        db.session.add(pastry)
        db.session.commit()
        
        assert Pastry.query.count() == 1
        assert Pastry.query.first().name == 'Croissant'