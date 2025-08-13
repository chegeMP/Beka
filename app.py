from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, timezone
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Application constants
DELIVERY_FEE = float(os.getenv('DELIVERY_FEE', 5.99))
COMPANY_EMAIL = os.getenv('COMPANY_EMAIL', 'orders@sweetdelights.com')
COMPANY_PHONE = os.getenv('COMPANY_PHONE', '(555) 123-4567')

# Database Models
class Pastry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(50))
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed deprecation warning

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed deprecation warning

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(100), nullable=False)
    delivery_postal_code = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed deprecation warning
    
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    pastry_id = db.Column(db.Integer, db.ForeignKey('pastry.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    pastry = db.relationship('Pastry', backref=db.backref('order_items', lazy=True))

def create_app(test_config=None):
    """Application factory pattern for testing"""
    app = Flask(__name__)
    
    # Use test config if provided, otherwise use your normal config
    if test_config:
        app.config.update(test_config)
    else:
        # Configuration from environment variables
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:lifeisgood@db:5432/pastry_db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Additional configuration
        app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
        app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
        app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register routes
    register_routes(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/')
    def index():
        featured_pastries = Pastry.query.filter_by(available=True).limit(6).all()
        return render_template('index.html', pastries=featured_pastries)

    @app.route('/browse')
    def browse():
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        query = Pastry.query.filter_by(available=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Pastry.name.ilike(f'%{search}%'))
        
        pastries = query.all()
        categories = db.session.query(Pastry.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        return render_template('browse.html', pastries=pastries, categories=categories, 
                             current_category=category, search_term=search)

    @app.route('/pastry/<int:pastry_id>')
    def pastry_detail(pastry_id):
        pastry = Pastry.query.get_or_404(pastry_id)
        return render_template('pastry_detail.html', pastry=pastry)

    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        pastry_id = int(request.form['pastry_id'])
        quantity = int(request.form['quantity'])
        
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        if str(pastry_id) in cart:
            cart[str(pastry_id)] += quantity
        else:
            cart[str(pastry_id)] = quantity
        
        session['cart'] = cart
        flash('Item added to cart!', 'success')
        return redirect(request.referrer or url_for('browse'))

    @app.route('/cart')
    def cart():
        if 'cart' not in session or not session['cart']:
            return render_template('cart.html', cart_items=[], total=0)
        
        cart_items = []
        total = 0
        
        for pastry_id, quantity in session['cart'].items():
            pastry = Pastry.query.get(int(pastry_id))
            if pastry:
                item_total = pastry.price * quantity
                total += item_total
                cart_items.append({
                    'pastry': pastry,
                    'quantity': quantity,
                    'item_total': item_total
                })
        
        return render_template('cart.html', cart_items=cart_items, total=total, delivery_fee=DELIVERY_FEE)

    @app.route('/update_cart', methods=['POST'])
    def update_cart():
        pastry_id = request.form['pastry_id']
        quantity = int(request.form['quantity'])
        
        if 'cart' in session:
            if quantity > 0:
                session['cart'][pastry_id] = quantity
            else:
                session['cart'].pop(pastry_id, None)
            session.modified = True
        
        return redirect(url_for('cart'))

    @app.route('/remove_from_cart/<int:pastry_id>')
    def remove_from_cart(pastry_id):
        if 'cart' in session:
            session['cart'].pop(str(pastry_id), None)
            session.modified = True
        return redirect(url_for('cart'))

    @app.route('/checkout')
    def checkout():
        if 'cart' not in session or not session['cart']:
            flash('Your cart is empty!', 'error')
            return redirect(url_for('browse'))
        
        cart_items = []
        total = 0
        
        for pastry_id, quantity in session['cart'].items():
            pastry = Pastry.query.get(int(pastry_id))
            if pastry:
                item_total = pastry.price * quantity
                total += item_total
                cart_items.append({
                    'pastry': pastry,
                    'quantity': quantity,
                    'item_total': item_total
                })
        
        # Generate delivery date options (next 14 days, excluding today)
        delivery_dates = []
        for i in range(1, 15):
            date = datetime.now().date() + timedelta(days=i)
            delivery_dates.append(date)
        
        return render_template('checkout.html', cart_items=cart_items, total=total, 
                             delivery_dates=delivery_dates, delivery_fee=DELIVERY_FEE)

    @app.route('/place_order', methods=['POST'])
    def place_order():
        try:
            # Get form data
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date()
            address = request.form['address']
            city = request.form['city']
            postal_code = request.form['postal_code']
            special_instructions = request.form.get('special_instructions', '')
            
            # Create or get customer
            customer = Customer.query.filter_by(email=email).first()
            if not customer:
                customer = Customer(name=name, email=email, phone=phone)
                db.session.add(customer)
                db.session.flush()
            
            # Calculate total
            total = 0
            for pastry_id, quantity in session['cart'].items():
                pastry = Pastry.query.get(int(pastry_id))
                if pastry:
                    total += pastry.price * quantity
            
            total += DELIVERY_FEE  # Add delivery fee
            
            # Create order
            order = Order(
                customer_id=customer.id,
                total_amount=total,
                delivery_date=delivery_date,
                delivery_address=address,
                delivery_city=city,
                delivery_postal_code=postal_code,
                special_instructions=special_instructions
            )
            db.session.add(order)
            db.session.flush()
            
            # Create order items
            for pastry_id, quantity in session['cart'].items():
                pastry = Pastry.query.get(int(pastry_id))
                if pastry:
                    order_item = OrderItem(
                        order_id=order.id,
                        pastry_id=pastry.id,
                        quantity=quantity,
                        unit_price=pastry.price
                    )
                    db.session.add(order_item)
            
            db.session.commit()
            
            # Clear cart
            session.pop('cart', None)
            
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_number=order.order_number))
        
        except Exception as e:
            db.session.rollback()
            flash('Error placing order. Please try again.', 'error')
            return redirect(url_for('checkout'))

    @app.route('/order/<order_number>')
    def order_confirmation(order_number):
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        return render_template('order_confirmation.html', order=order, delivery_fee=DELIVERY_FEE)

    @app.route('/api/pastries')
    def api_pastries():
        pastries = Pastry.query.filter_by(available=True).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'image_url': p.image_url,
            'category': p.category
        } for p in pastries])

# Create the app instance for production
app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))