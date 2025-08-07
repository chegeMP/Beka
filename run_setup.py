# run_setup.py - Standalone database initialization script
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lifeisgood@localhost/pastry_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Pastry model (simplified for initialization)
class Pastry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(50))
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(36), unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(100), nullable=False)
    delivery_postal_code = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    pastry_id = db.Column(db.Integer, db.ForeignKey('pastry.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    pastry = db.relationship('Pastry', backref=db.backref('order_items', lazy=True))

def initialize_database():
    """Initialize the database with sample data"""
    
    with app.app_context():
        print("Creating database tables...")
        # Create all tables
        db.create_all()
        
        # Check if pastries already exist
        if Pastry.query.count() > 0:
            print("Database already contains pastries. Skipping initialization.")
            return
        
        print("Adding sample pastries...")
        
        # Sample pastry data with realistic descriptions and categories
        sample_pastries = [
            {
                'name': 'Chocolate Croissant',
                'description': 'Buttery, flaky croissant filled with rich Belgian dark chocolate. Made with premium French butter and artisanal chocolate for an indulgent morning treat.',
                'price': 3.50,
                'category': 'Croissants',
                'image_url': 'https://images.unsplash.com/photo-1555507036-ab794f4ded6a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Blueberry Muffin',
                'description': 'Moist vanilla muffin bursting with fresh Maine blueberries. Topped with a golden crumb topping and baked to perfection each morning.',
                'price': 2.75,
                'category': 'Muffins',
                'image_url': 'https://images.unsplash.com/photo-1571115764595-644a1f56a55c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Apple Danish',
                'description': 'Traditional Danish pastry with layers of buttery puff pastry, filled with cinnamon-spiced apple compote and finished with a sweet vanilla glaze.',
                'price': 4.25,
                'category': 'Danish',
                'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Strawberry Tart',
                'description': 'Elegant French pastry featuring a crisp almond tart shell filled with silky vanilla pastry cream and topped with fresh strawberries and apricot glaze.',
                'price': 5.50,
                'category': 'Tarts',
                'image_url': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Almond Croissant',
                'description': 'Classic French croissant filled with rich almond cream and topped with sliced almonds and powdered sugar. A bakery favorite since 1985.',
                'price': 4.00,
                'category': 'Croissants',
                'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Lemon Eclair',
                'description': 'Light choux pastry filled with tangy lemon curd and topped with bright lemon glaze. A refreshing citrus treat perfect for any time of day.',
                'price': 3.75,
                'category': 'Eclairs',
                'image_url': 'https://images.unsplash.com/photo-1486427944299-d1955d23e34d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Chocolate Brownie',
                'description': 'Decadent fudge brownie made with premium cocoa and studded with toasted walnuts. Rich, dense texture with a crackly top.',
                'price': 3.25,
                'category': 'Brownies',
                'image_url': 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Raspberry Cheesecake',
                'description': 'Creamy New York style cheesecake with a graham cracker crust, swirled with fresh raspberry puree and topped with fresh berries.',
                'price': 6.00,
                'category': 'Cheesecakes',
                'image_url': 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Cinnamon Roll',
                'description': 'Soft, pillowy sweet roll filled with brown sugar and cinnamon, topped with house-made cream cheese frosting. Best served warm.',
                'price': 3.00,
                'category': 'Rolls',
                'image_url': 'https://images.unsplash.com/photo-1509365390234-d5681ebb4062?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Mixed Berry Scone',
                'description': 'Traditional British scone loaded with blueberries, raspberries, and blackberries. Served with clotted cream and strawberry jam.',
                'price': 2.95,
                'category': 'Scones',
                'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Tiramisu Slice',
                'description': 'Classic Italian dessert with layers of espresso-soaked ladyfingers and rich mascarpone cream, dusted with cocoa powder.',
                'price': 5.75,
                'category': 'Cakes',
                'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Pecan Pie Slice',
                'description': 'Southern classic with a flaky butter crust filled with rich, gooey pecan filling made with pure maple syrup and toasted pecans.',
                'price': 4.50,
                'category': 'Pies',
                'image_url': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Lemon Tart',
                'description': 'Bright and tangy lemon curd in a crisp pastry shell, topped with torched meringue. Made with fresh lemons and organic eggs.',
                'price': 4.95,
                'category': 'Tarts',
                'image_url': 'https://images.unsplash.com/photo-1519915028121-7d3463d20b13?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'Red Velvet Cupcake',
                'description': 'Moist red velvet cake topped with classic cream cheese frosting and a sprinkle of red velvet crumbs. A Southern favorite.',
                'price': 3.75,
                'category': 'Cupcakes',
                'image_url': 'https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            },
            {
                'name': 'French Macarons',
                'description': 'Delicate almond-based cookies with smooth tops and ruffled feet, filled with ganache. Available in vanilla, chocolate, and raspberry flavors.',
                'price': 2.25,
                'category': 'Macarons',
                'image_url': 'https://images.unsplash.com/photo-1558312657-b2dead66fad7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            }
        ]
        
        # Add pastries to database
        for pastry_data in sample_pastries:
            pastry = Pastry(
                name=pastry_data['name'],
                description=pastry_data['description'],
                price=pastry_data['price'],
                category=pastry_data['category'],
                image_url=pastry_data['image_url'],
                available=True
            )
            db.session.add(pastry)
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully added {len(sample_pastries)} pastries to the database!")
        print("Database initialization complete!")

if __name__ == '__main__':
    # Update these with your actual database credentials
    print("IMPORTANT: Make sure to update the database connection string in this file!")
    print("Current connection string: postgresql://postgres:lifeisgood@localhost/pastry_db")
    print()
    
    response = input("Have you updated the database connection string? (y/n): ")
    if response.lower() != 'y':
        print("Please update the database connection string and run again.")
        sys.exit(1)
    
    initialize_database()