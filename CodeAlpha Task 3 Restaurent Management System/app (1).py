from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Using an in-memory SQLite database for a lightweight, zero-setup run
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 🗄️ DATABASE MODELS
# ==========================================

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    reservation_time = db.Column(db.String(50), nullable=False) # Format: YYYY-MM-DD HH:MM
    guests = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), nullable=True)
    status = db.Column(db.String(20), default='Pending') # Pending, Preparing, Served, Paid
    
    # Relationship to access ordered items easily
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)


# ==========================================
# ⚙️ API ROUTES & LOGIC
# ==========================================

# 1. View Menu Items
@app.route('/api/menu', methods=['GET'])
def get_menu():
    menu = MenuItem.query.all()
    return jsonify([{"id": item.id, "name": item.name, "price": item.price} for item in menu])

# 2. View Table Availability Check
@app.route('/api/tables/available', methods=['GET'])
def get_available_tables():
    tables = Table.query.filter_by(is_available=True).all()
    return jsonify([{"id": t.id, "table_number": t.table_number, "capacity": t.capacity} for t in tables])

# 3. Reserve a Table (with capacity check)
@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.json
    table = Table.query.get(data['table_id'])
    
    if not table:
        return jsonify({"error": "Table not found"}), 404
    if not table.is_available:
        return jsonify({"error": "Table is currently occupied or unavailable"}), 400
    if data['guests'] > table.capacity:
        return jsonify({"error": f"Table capacity exceeded. Max seats: {table.capacity}"}), 400

    new_res = Reservation(
        table_id=data['table_id'],
        customer_name=data['customer_name'],
        reservation_time=data['reservation_time'],
        guests=data['guests']
    )
    db.session.add(new_res)
    db.session.commit()
    return jsonify({"message": "Reservation successful!", "reservation_id": new_res.id}), 201

# 4. Place Order & Auto-Update Inventory (Fixed for transactional/session safety)
@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.json  # Expected structure: {"table_id": 1, "items": [{"menu_item_id": 1, "quantity": 2}]}
    
    # Phase 1: Validate EVERYTHING before altering the DB session state
    validated_items = []
    for item in data['items']:
        menu_item = MenuItem.query.get(item['menu_item_id'])
        if not menu_item:
            return jsonify({"error": f"Menu item ID {item['menu_item_id']} not found"}), 404
            
        inventory_stock = InventoryItem.query.filter_by(name=menu_item.name).first()
        if inventory_stock and inventory_stock.quantity < item['quantity']:
            return jsonify({"error": f"Insufficient stock for {menu_item.name}. Available: {inventory_stock.quantity}"}), 400
        
        # Keep track of validated details to update in the next safe loop execution
        validated_items.append((inventory_stock, item['quantity'], menu_item.id))

    # Phase 2: Create active records only when all validation parameters clear successfully
    new_order = Order(table_id=data.get('table_id'))
    db.session.add(new_order)
    db.session.commit() # Save the order record to fetch a unique order.id primary key

    for inventory_stock, quantity, menu_item_id in validated_items:
        if inventory_stock:
            inventory_stock.quantity -= quantity # Safely deduct inventory stock counts
        
        order_item = OrderItem(order_id=new_order.id, menu_item_id=menu_item_id, quantity=quantity)
        db.session.add(order_item)
        
    db.session.commit()
    return jsonify({"message": "Order placed successfully!", "order_id": new_order.id}), 201

# 5. View Current Inventory Status
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    inventory = InventoryItem.query.all()
    return jsonify([{"id": idx.id, "name": idx.name, "quantity": idx.quantity} for idx in inventory])

# 6. Update Table Details (Capacity and Table Number)
@app.route('/api/tables/<int:table_id>', methods=['PUT'])
def update_table(table_id):
    data = request.json
    # Find the table record matching the unique table ID primary key
    table = Table.query.get(table_id)
    
    if not table:
        return jsonify({"error": f"Table with ID {table_id} not found"}), 404

    # Update Table Number (if provided in the JSON payload body structure)
    if 'table_number' in data:
        # Enforce uniqueness constraint mapping logic
        existing_table = Table.query.filter_by(table_number=data['table_number']).first()
        if existing_table and existing_table.id != table.id:
            return jsonify({"error": f"Table number {data['table_number']} is already assigned to another table"}), 400
        table.table_number = data['table_number']

    # Update Capacity (if provided in the JSON payload body structure)
    if 'capacity' in data:
        if data['capacity'] <= 0:
            return jsonify({"error": "Capacity must be greater than 0"}), 400
        table.capacity = data['capacity']

    # Persist the transactional changes to the SQLite engine safely
    db.session.commit()
    
    return jsonify({
        "message": f"Table {table.id} updated successfully!",
        "table": {
            "id": table.id,
            "table_number": table.table_number,
            "capacity": table.capacity,
            "is_available": table.is_available
        }
    }), 200


# ==========================================
# 🚀 SEED DATA & SERVER INITIALIZATION
# ==========================================

def seed_initial_data():
    """Pre-populates the database engine with baseline mock elements for testing."""
    # Tables
    db.session.add_all([
        Table(table_number=1, capacity=2, is_available=True),
        Table(table_number=2, capacity=4, is_available=True),
        Table(table_number=3, capacity=6, is_available=False)
    ])
    # Menu Items
    db.session.add_all([
        MenuItem(name="Pasta", price=12.99),
        MenuItem(name="Burger", price=8.99),
        MenuItem(name="Pizza", price=15.50)
    ])
    # Inventory items mapped to corresponding food strings to process auto-updates
    db.session.add_all([
        InventoryItem(name="Pasta", quantity=20),
        InventoryItem(name="Burger", quantity=5),
        InventoryItem(name="Pizza", quantity=15)
    ])
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_initial_data()
    # Explicitly links straight to your primary active routing check
    print("🚀 Restaurant Backend Server Running at http://127.0.0.1:5000/api/tables/available")
    app.run(debug=True)
