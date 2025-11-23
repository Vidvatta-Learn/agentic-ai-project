"""
Extended Setup script to create comprehensive SmartScribble SQLite database
Includes: customers, orders, products, support_tickets, reviews, returns, shipments
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random


def setup_extended_database(db_path='smartscribble_extended.db'):
    """
    Setup the comprehensive SmartScribble SQLite database

    Args:
        db_path: Path to the SQLite database file
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_db_path = os.path.join(script_dir, db_path)

    # Remove existing database if it exists
    if os.path.exists(full_db_path):
        print(f"Removing existing database at {full_db_path}...")
        os.remove(full_db_path)

    print(f"Creating new database at {full_db_path}...")

    try:
        conn = sqlite3.connect(full_db_path)
        cursor = conn.cursor()
        print("✓ Database created successfully!")

        # ==================== CUSTOMERS TABLE ====================
        print("\n1. Creating customers table...")
        cursor.execute('''
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address_line1 TEXT,
                address_line2 TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                postal_code TEXT,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                customer_status TEXT DEFAULT 'active' CHECK (customer_status IN ('active', 'inactive', 'suspended')),
                total_purchases REAL DEFAULT 0.00,
                loyalty_points INTEGER DEFAULT 0,
                preferred_language TEXT DEFAULT 'English',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Customers table created!")

        # ==================== PRODUCTS TABLE ====================
        print("2. Creating products table...")
        cursor.execute('''
            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                product_sku TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                unit_price REAL NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 10,
                is_active INTEGER DEFAULT 1,
                release_date TEXT,
                warranty_months INTEGER DEFAULT 12,
                weight_kg REAL,
                dimensions TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Products table created!")

        # ==================== ORDERS TABLE ====================
        print("3. Creating orders table...")
        cursor.execute('''
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_number TEXT UNIQUE NOT NULL,
                order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                discount_amount REAL DEFAULT 0.00,
                tax_amount REAL DEFAULT 0.00,
                shipping_cost REAL DEFAULT 0.00,
                final_amount REAL NOT NULL,
                order_status TEXT DEFAULT 'pending' CHECK (order_status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded', 'returned')),
                payment_method TEXT,
                payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
                shipping_address_line1 TEXT,
                shipping_address_line2 TEXT,
                shipping_city TEXT,
                shipping_state TEXT,
                shipping_country TEXT,
                shipping_postal_code TEXT,
                estimated_delivery_date TEXT,
                actual_delivery_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        print("✓ Orders table created!")

        # ==================== SHIPMENTS TABLE ====================
        print("4. Creating shipments table...")
        cursor.execute('''
            CREATE TABLE shipments (
                shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                tracking_number TEXT UNIQUE NOT NULL,
                carrier TEXT NOT NULL,
                shipping_method TEXT,
                shipped_date TEXT,
                estimated_arrival TEXT,
                actual_arrival TEXT,
                current_location TEXT,
                shipment_status TEXT DEFAULT 'preparing' CHECK (shipment_status IN ('preparing', 'in_transit', 'out_for_delivery', 'delivered', 'failed', 'returned')),
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        ''')
        print("✓ Shipments table created!")

        # ==================== SUPPORT TICKETS TABLE ====================
        print("5. Creating support_tickets table...")
        cursor.execute('''
            CREATE TABLE support_tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                order_id INTEGER,
                subject TEXT NOT NULL,
                category TEXT NOT NULL CHECK (category IN ('Technical', 'Billing', 'Shipping', 'Product Inquiry', 'Return/Refund', 'Other')),
                priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
                status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
                description TEXT NOT NULL,
                resolution TEXT,
                assigned_to TEXT,
                opened_date TEXT DEFAULT CURRENT_TIMESTAMP,
                closed_date TEXT,
                first_response_time_minutes INTEGER,
                resolution_time_minutes INTEGER,
                satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        ''')
        print("✓ Support tickets table created!")

        # ==================== TICKET MESSAGES TABLE ====================
        print("6. Creating ticket_messages table...")
        cursor.execute('''
            CREATE TABLE ticket_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL CHECK (sender_type IN ('customer', 'agent', 'system')),
                sender_name TEXT,
                message_text TEXT NOT NULL,
                is_internal INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id) ON DELETE CASCADE
            )
        ''')
        print("✓ Ticket messages table created!")

        # ==================== PRODUCT REVIEWS TABLE ====================
        print("7. Creating product_reviews table...")
        cursor.execute('''
            CREATE TABLE product_reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                order_id INTEGER,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_title TEXT,
                review_text TEXT,
                is_verified_purchase INTEGER DEFAULT 0,
                helpful_count INTEGER DEFAULT 0,
                reported_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        ''')
        print("✓ Product reviews table created!")

        # ==================== RETURNS TABLE ====================
        print("8. Creating returns table...")
        cursor.execute('''
            CREATE TABLE returns (
                return_id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_number TEXT UNIQUE NOT NULL,
                order_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                return_reason TEXT NOT NULL,
                return_type TEXT NOT NULL CHECK (return_type IN ('refund', 'exchange', 'warranty')),
                return_status TEXT DEFAULT 'requested' CHECK (return_status IN ('requested', 'approved', 'rejected', 'received', 'processing', 'completed')),
                quantity INTEGER NOT NULL DEFAULT 1,
                refund_amount REAL,
                return_shipping_label TEXT,
                requested_date TEXT DEFAULT CURRENT_TIMESTAMP,
                approved_date TEXT,
                received_date TEXT,
                completed_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        print("✓ Returns table created!")

        # ==================== INVENTORY LOGS TABLE ====================
        print("9. Creating inventory_logs table...")
        cursor.execute('''
            CREATE TABLE inventory_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                change_type TEXT NOT NULL CHECK (change_type IN ('restock', 'sale', 'return', 'damage', 'adjustment')),
                quantity_change INTEGER NOT NULL,
                quantity_before INTEGER NOT NULL,
                quantity_after INTEGER NOT NULL,
                reference_id INTEGER,
                reference_type TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        print("✓ Inventory logs table created!")

        # ==================== PROMOTIONS TABLE ====================
        print("10. Creating promotions table...")
        cursor.execute('''
            CREATE TABLE promotions (
                promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                promotion_code TEXT UNIQUE NOT NULL,
                promotion_name TEXT NOT NULL,
                discount_type TEXT NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount')),
                discount_value REAL NOT NULL,
                min_purchase_amount REAL DEFAULT 0.00,
                max_discount_amount REAL,
                applicable_products TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                usage_limit INTEGER,
                usage_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Promotions table created!")

        # ==================== CREATE INDEXES ====================
        print("\n11. Creating indexes...")
        indexes = [
            'CREATE INDEX idx_customers_email ON customers(email)',
            'CREATE INDEX idx_customers_status ON customers(customer_status)',
            'CREATE INDEX idx_orders_customer_id ON orders(customer_id)',
            'CREATE INDEX idx_orders_order_number ON orders(order_number)',
            'CREATE INDEX idx_orders_status ON orders(order_status)',
            'CREATE INDEX idx_orders_date ON orders(order_date)',
            'CREATE INDEX idx_shipments_order_id ON shipments(order_id)',
            'CREATE INDEX idx_shipments_tracking ON shipments(tracking_number)',
            'CREATE INDEX idx_tickets_customer_id ON support_tickets(customer_id)',
            'CREATE INDEX idx_tickets_status ON support_tickets(status)',
            'CREATE INDEX idx_tickets_category ON support_tickets(category)',
            'CREATE INDEX idx_reviews_product_id ON product_reviews(product_id)',
            'CREATE INDEX idx_reviews_customer_id ON product_reviews(customer_id)',
            'CREATE INDEX idx_returns_order_id ON returns(order_id)',
            'CREATE INDEX idx_returns_status ON returns(return_status)',
        ]
        for idx_sql in indexes:
            cursor.execute(idx_sql)
        print("✓ All indexes created!")

        # ==================== INSERT PRODUCTS ====================
        print("\n12. Inserting products...")
        products_data = [
            ('SmartScribble AI Notebook', 'SSAI-NB-001', 'Hardware', 'Revolutionary AI-powered digital notebook with E-ink display and pressure-sensitive stylus', 299.00, 500, 50, 1, '2024-01-01', 12, 0.395, '230mm x 190mm x 5.8mm'),
            ('Replacement Stylus', 'SSAI-STY-001', 'Accessory', 'Pressure-sensitive replacement stylus with 4096 levels of pressure', 29.00, 1000, 100, 1, '2024-01-01', 6, 0.015, '140mm length'),
            ('Premium Leather Folio', 'SSAI-FOL-001', 'Accessory', 'Handcrafted leather folio case with document pocket', 79.00, 200, 25, 1, '2024-02-01', 12, 0.250, '250mm x 210mm x 15mm'),
            ('Screen Protector (2-pack)', 'SSAI-SP-001', 'Accessory', 'Anti-glare tempered glass screen protector', 19.00, 500, 50, 1, '2024-01-01', 0, 0.050, '230mm x 190mm'),
            ('USB-C Charging Cable', 'SSAI-CAB-001', 'Accessory', 'Braided USB-C charging cable 2m', 15.00, 800, 100, 1, '2024-01-01', 12, 0.080, '2000mm length'),
            ('Replacement Nibs (10-pack)', 'SSAI-NIB-001', 'Accessory', 'Felt-composite replacement nibs for stylus', 12.00, 600, 75, 1, '2024-01-01', 0, 0.010, '5mm diameter'),
            ('ScribbleCare+ Protection Plan', 'SSAI-CARE-001', 'Service', '2-year accidental damage protection', 49.00, 9999, 0, 1, '2024-01-01', 24, 0.0, 'Digital Service'),
        ]
        cursor.executemany('''
            INSERT INTO products (product_name, product_sku, category, description, unit_price, stock_quantity, reorder_level, is_active, release_date, warranty_months, weight_kg, dimensions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', products_data)
        print(f"✓ Inserted {len(products_data)} products!")

        # ==================== INSERT CUSTOMERS ====================
        print("13. Inserting 20 customers...")
        customers_data = [
            ('Sarah', 'Johnson', 'sarah.johnson@email.com', '+1-555-0101', '123 Maple Street', 'Apt 4B', 'New York', 'NY', 'USA', '10001', '2024-01-15 10:30:00', '2025-01-20 14:22:00', 'active', 'English', 'VIP customer, frequent purchaser'),
            ('Michael', 'Chen', 'michael.chen@email.com', '+1-555-0102', '456 Oak Avenue', None, 'San Francisco', 'CA', 'USA', '94102', '2024-02-20 09:15:00', '2025-01-18 16:45:00', 'active', 'English', 'Tech enthusiast'),
            ('Emily', 'Rodriguez', 'emily.rodriguez@email.com', '+1-555-0103', '789 Pine Road', 'Suite 201', 'Austin', 'TX', 'USA', '73301', '2024-03-10 11:20:00', '2025-01-15 09:30:00', 'active', 'Spanish', 'Artist, loves sketching features'),
            ('David', 'Kim', 'david.kim@email.com', '+1-555-0104', '321 Elm Street', None, 'Seattle', 'WA', 'USA', '98101', '2024-04-05 14:45:00', '2025-01-21 11:15:00', 'active', 'Korean', None),
            ('Jessica', 'Patel', 'jessica.patel@email.com', '+1-555-0105', '654 Birch Lane', 'Unit 3', 'Boston', 'MA', 'USA', '02101', '2024-05-12 08:30:00', '2025-01-19 13:20:00', 'active', 'English', 'Educator, bulk purchaser for classroom'),
            ('James', 'Williams', 'james.williams@email.com', '+1-555-0106', '987 Cedar Drive', None, 'Chicago', 'IL', 'USA', '60601', '2024-06-18 16:00:00', '2025-01-17 10:45:00', 'active', 'English', None),
            ('Amanda', 'Taylor', 'amanda.taylor@email.com', '+1-555-0107', '147 Willow Court', 'Apt 12', 'Denver', 'CO', 'USA', '80201', '2024-07-22 12:15:00', '2025-01-22 15:30:00', 'active', 'English', 'Requested refund once, resolved'),
            ('Christopher', 'Lee', 'christopher.lee@email.com', '+1-555-0108', '258 Spruce Avenue', None, 'Portland', 'OR', 'USA', '97201', '2024-08-08 10:45:00', '2025-01-16 12:00:00', 'active', 'English', None),
            ('Rachel', 'Martinez', 'rachel.martinez@email.com', '+1-555-0109', '369 Aspen Boulevard', 'Suite 5', 'Miami', 'FL', 'USA', '33101', '2024-09-14 13:30:00', '2025-01-14 08:15:00', 'active', 'Spanish', 'Business owner, multiple devices'),
            ('Daniel', 'Anderson', 'daniel.anderson@email.com', '+1-555-0110', '741 Poplar Street', None, 'Atlanta', 'GA', 'USA', '30301', '2024-10-20 09:00:00', '2025-01-13 16:45:00', 'active', 'English', None),
            ('Lauren', 'Thomas', 'lauren.thomas@email.com', '+1-555-0111', '852 Hickory Road', 'Apt 8', 'Phoenix', 'AZ', 'USA', '85001', '2024-11-05 15:20:00', '2025-01-12 14:30:00', 'active', 'English', 'Student discount applied'),
            ('Ryan', 'Jackson', 'ryan.jackson@email.com', '+1-555-0112', '963 Magnolia Lane', None, 'Philadelphia', 'PA', 'USA', '19101', '2024-11-18 11:45:00', '2025-01-21 09:00:00', 'active', 'English', None),
            ('Nicole', 'White', 'nicole.white@email.com', '+1-555-0113', '159 Sycamore Drive', 'Unit 7', 'San Diego', 'CA', 'USA', '92101', '2024-12-01 08:15:00', '2025-01-20 11:30:00', 'active', 'English', 'Only purchased replacement stylus'),
            ('Kevin', 'Harris', 'kevin.harris@email.com', '+1-555-0114', '357 Redwood Circle', None, 'Dallas', 'TX', 'USA', '75201', '2024-12-10 14:30:00', '2025-01-19 15:45:00', 'active', 'English', None),
            ('Stephanie', 'Clark', 'stephanie.clark@email.com', '+1-555-0115', '486 Cypress Court', 'Apt 15', 'Minneapolis', 'MN', 'USA', '55401', '2024-12-15 10:00:00', '2025-01-18 10:15:00', 'active', 'English', 'Pre-ordered, not yet shipped'),
            ('Brian', 'Lewis', 'brian.lewis@email.com', '+1-555-0116', '753 Juniper Street', None, 'Detroit', 'MI', 'USA', '48201', '2025-01-02 12:45:00', '2025-01-22 13:00:00', 'active', 'English', None),
            ('Michelle', 'Walker', 'michelle.walker@email.com', '+1-555-0117', '864 Oakwood Avenue', 'Suite 3', 'Tampa', 'FL', 'USA', '33601', '2025-01-08 09:30:00', '2025-01-21 16:20:00', 'active', 'English', None),
            ('Jason', 'Hall', 'jason.hall@email.com', '+1-555-0118', '975 Beech Road', None, 'Las Vegas', 'NV', 'USA', '89101', '2025-01-12 16:15:00', '2025-01-20 14:45:00', 'active', 'English', 'Returned one item, exchanged successfully'),
            ('Megan', 'Allen', 'megan.allen@email.com', '+1-555-0119', '246 Palm Drive', 'Apt 6', 'Orlando', 'FL', 'USA', '32801', '2025-01-15 11:00:00', '2025-01-19 09:30:00', 'active', 'English', None),
            ('Andrew', 'Young', 'andrew.young@email.com', '+1-555-0120', '135 Walnut Lane', None, 'Charlotte', 'NC', 'USA', '28201', '2025-01-18 13:45:00', '2025-01-22 12:15:00', 'active', 'English', 'Purchased two replacement styluses'),
        ]
        cursor.executemany('''
            INSERT INTO customers (first_name, last_name, email, phone, address_line1, address_line2, city, state, country, postal_code, registration_date, last_login, customer_status, preferred_language, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', customers_data)
        print(f"✓ Inserted {len(customers_data)} customers!")

        # ==================== INSERT ORDERS ====================
        print("14. Inserting 100 orders...")
        orders_sample = [
            # Customer 1 - 5 orders
            (1, 'SSN-20240115-0001', '2024-01-15 10:45:00', 1, 1, 299.00, 299.00, 0.00, 26.91, 0.00, 325.91, 'delivered', 'Credit Card', 'paid', '123 Maple Street', None, 'New York', 'NY', 'USA', '10001', '2024-01-20', '2024-01-19', None),
            (1, 'SSN-20240220-0002', '2024-02-20 14:30:00', 2, 1, 29.00, 29.00, 0.00, 2.61, 5.00, 36.61, 'delivered', 'Credit Card', 'paid', '123 Maple Street', None, 'New York', 'NY', 'USA', '10001', '2024-02-25', '2024-02-24', None),
            (1, 'SSN-20240515-0003', '2024-05-15 09:15:00', 1, 1, 299.00, 299.00, 29.90, 24.21, 0.00, 293.31, 'delivered', 'Credit Card', 'paid', '123 Maple Street', None, 'New York', 'NY', 'USA', '10001', '2024-05-20', '2024-05-18', None),
            (1, 'SSN-20240820-0004', '2024-08-20 16:45:00', 2, 1, 29.00, 29.00, 0.00, 2.61, 5.00, 36.61, 'delivered', 'PayPal', 'paid', '123 Maple Street', None, 'New York', 'NY', 'USA', '10001', '2024-08-25', '2024-08-23', None),
            (1, 'SSN-20241110-0005', '2024-11-10 11:30:00', 2, 1, 29.00, 29.00, 0.00, 2.61, 5.00, 36.61, 'delivered', 'Credit Card', 'paid', '123 Maple Street', None, 'New York', 'NY', 'USA', '10001', '2024-11-15', '2024-11-14', None),
            # Customer 7 - refund case
            (7, 'SSN-20240722-0006', '2024-07-22 12:30:00', 1, 1, 299.00, 299.00, 0.00, 26.91, 0.00, 325.91, 'refunded', 'Credit Card', 'refunded', '147 Willow Court', 'Apt 12', 'Denver', 'CO', 'USA', '80201', '2024-07-27', '2024-07-26', 'Display issue reported'),
        ]

        # Generate 93 more orders distributed across customers
        for i in range(7, 100):
            customer_id = (i % 20) + 1
            order_num = f'SSN-20240{random.randint(1,12):02d}{random.randint(10,28):02d}-{i:04d}'
            order_date = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 385))).strftime('%Y-%m-%d %H:%M:%S')
            product_id = random.choice([1, 2, 2, 2, 3, 4, 5, 6])  # More stylus orders
            quantity = 1

            # Get product price
            if product_id == 1:
                unit_price = 299.00
            elif product_id == 2:
                unit_price = 29.00
            elif product_id == 3:
                unit_price = 79.00
            elif product_id == 4:
                unit_price = 19.00
            elif product_id == 5:
                unit_price = 15.00
            elif product_id == 6:
                unit_price = 12.00
            else:
                unit_price = 49.00

            total = unit_price * quantity
            discount = 29.90 if (product_id == 1 and random.random() < 0.1) else 0.00
            tax = (total - discount) * 0.09
            shipping = 0.00 if product_id == 1 else 5.00
            final = total - discount + tax + shipping

            status = random.choice(['delivered'] * 7 + ['shipped', 'processing', 'pending'])
            payment_status = 'paid' if status in ['delivered', 'shipped', 'processing'] else 'pending'
            delivery = (datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S') + timedelta(days=5)).strftime('%Y-%m-%d') if status == 'delivered' else None

            orders_sample.append((
                customer_id, order_num, order_date, product_id, quantity, unit_price, total,
                discount, tax, shipping, final, status, 'Credit Card', payment_status,
                '123 Main St', None, 'City', 'ST', 'USA', '12345',
                (datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S') + timedelta(days=5)).strftime('%Y-%m-%d'),
                delivery, None
            ))

        cursor.executemany('''
            INSERT INTO orders (customer_id, order_number, order_date, product_id, quantity, unit_price, total_amount, discount_amount, tax_amount, shipping_cost, final_amount, order_status, payment_method, payment_status, shipping_address_line1, shipping_address_line2, shipping_city, shipping_state, shipping_country, shipping_postal_code, estimated_delivery_date, actual_delivery_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', orders_sample)
        print(f"✓ Inserted {len(orders_sample)} orders!")

        # ==================== INSERT SHIPMENTS ====================
        print("15. Inserting shipment records...")
        cursor.execute("SELECT order_id, order_number, order_status FROM orders WHERE order_status IN ('shipped', 'delivered')")
        shipped_orders = cursor.fetchall()

        shipments_data = []
        carriers = ['FedEx', 'UPS', 'USPS', 'DHL']
        for idx, (order_id, order_num, status) in enumerate(shipped_orders[:50], 1):  # First 50
            tracking = f'TRK{random.randint(100000000, 999999999)}'
            carrier = random.choice(carriers)
            shipped_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            arrival = (datetime.strptime(shipped_date, '%Y-%m-%d') + timedelta(days=5)).strftime('%Y-%m-%d')
            actual = arrival if status == 'delivered' else None
            shipment_status = 'delivered' if status == 'delivered' else 'in_transit'

            shipments_data.append((
                order_id, tracking, carrier, 'Standard', shipped_date, arrival, actual,
                f'{carrier} Distribution Center', shipment_status, None
            ))

        cursor.executemany('''
            INSERT INTO shipments (order_id, tracking_number, carrier, shipping_method, shipped_date, estimated_arrival, actual_arrival, current_location, shipment_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', shipments_data)
        print(f"✓ Inserted {len(shipments_data)} shipments!")

        # ==================== INSERT SUPPORT TICKETS ====================
        print("16. Inserting support tickets...")
        tickets_data = [
            (1, 'TKT-2024-0001', 1, 1, 'Display not turning on', 'Technical', 'high', 'resolved', 'Device won\'t power on after charging overnight', 'Sent replacement unit', 'Agent Smith', '2024-01-20 09:00:00', '2024-01-22 16:30:00', 45, 3270, 5),
            (2, 'TKT-2024-0002', 3, None, 'How to sync with Evernote?', 'Product Inquiry', 'low', 'closed', 'Need help setting up Evernote sync', 'Provided setup guide link', 'Agent Johnson', '2024-03-15 14:20:00', '2024-03-15 15:45:00', 15, 85, 5),
            (3, 'TKT-2024-0003', 7, 6, 'Request refund for defective unit', 'Return/Refund', 'high', 'resolved', 'Display has dead pixels, requesting refund', 'Refund processed, return label sent', 'Agent Davis', '2024-07-23 10:00:00', '2024-07-28 14:00:00', 60, 7140, 4),
            (4, 'TKT-2024-0004', 5, 19, 'Order not received', 'Shipping', 'urgent', 'resolved', 'Order was supposed to arrive 3 days ago', 'Located package, delivered next day', 'Agent Martinez', '2024-05-20 08:30:00', '2024-05-21 17:00:00', 30, 1950, 4),
            (5, 'TKT-2024-0005', 12, None, 'Stylus not pairing', 'Technical', 'medium', 'closed', 'Replacement stylus doesn\'t seem to work', 'Guided through reset process', 'Agent Lee', '2024-12-18 11:00:00', '2024-12-18 12:30:00', 20, 90, 5),
            (6, 'TKT-2025-0006', 9, None, 'Bulk discount inquiry', 'Billing', 'low', 'closed', 'Want to purchase 10 units for office, any discounts?', 'Provided enterprise sales contact', 'Agent Wilson', '2025-01-10 09:45:00', '2025-01-10 10:15:00', 10, 30, 5),
            (7, 'TKT-2025-0007', 18, 36, 'Exchange for new unit', 'Return/Refund', 'medium', 'in_progress', 'Stylus tracking issue, want exchange', 'Processing exchange', 'Agent Brown', '2025-01-13 14:00:00', None, 25, None, None),
            (8, 'TKT-2025-0008', 15, 26, 'When will pre-order ship?', 'Shipping', 'low', 'open', 'Pre-ordered in December, need shipping date', None, 'Agent Taylor', '2025-01-20 16:00:00', None, None, None, None),
        ]

        cursor.executemany('''
            INSERT INTO support_tickets (ticket_id, ticket_number, customer_id, order_id, subject, category, priority, status, description, resolution, assigned_to, opened_date, closed_date, first_response_time_minutes, resolution_time_minutes, satisfaction_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tickets_data)
        print(f"✓ Inserted {len(tickets_data)} support tickets!")

        # ==================== INSERT TICKET MESSAGES ====================
        print("17. Inserting ticket messages...")
        messages_data = [
            (1, 'customer', 'Sarah Johnson', 'My device won\'t turn on. I charged it all night but nothing happens when I press the power button.', 0, '2024-01-20 09:00:00'),
            (1, 'agent', 'Agent Smith', 'Thank you for contacting us. Let\'s try a hard reset. Please hold the power button for 30 seconds.', 0, '2024-01-20 09:45:00'),
            (1, 'customer', 'Sarah Johnson', 'I tried that but still nothing. The LED doesn\'t even light up.', 0, '2024-01-20 10:15:00'),
            (1, 'agent', 'Agent Smith', 'I apologize for the inconvenience. This appears to be a hardware issue. I\'m approving a replacement unit to be shipped immediately.', 0, '2024-01-20 11:00:00'),
            (2, 'customer', 'Emily Rodriguez', 'I just got my SmartScribble and want to sync with Evernote. Where do I find this setting?', 0, '2024-03-15 14:20:00'),
            (2, 'agent', 'Agent Johnson', 'Go to Settings > Cloud Sync > Add Service > Select Evernote. You\'ll need to authorize the connection. Here\'s a detailed guide: [link]', 0, '2024-03-15 14:35:00'),
            (3, 'customer', 'Amanda Taylor', 'I received the device but the display has several dead pixels in the center. This is unusable. I want a refund.', 0, '2024-07-23 10:00:00'),
            (3, 'agent', 'Agent Davis', 'I\'m very sorry to hear that. We stand behind our quality. I\'m processing your refund right away and emailing you a prepaid return label.', 0, '2024-07-23 11:00:00'),
        ]

        cursor.executemany('''
            INSERT INTO ticket_messages (ticket_id, sender_type, sender_name, message_text, is_internal, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', messages_data)
        print(f"✓ Inserted {len(messages_data)} ticket messages!")

        # ==================== INSERT PRODUCT REVIEWS ====================
        print("18. Inserting product reviews...")
        reviews_data = [
            (1, 1, 1, 5, 'Life-changing productivity tool!', 'I\'ve been using this for 3 months and it\'s transformed how I take notes. The AI features are incredible.', 1, 45, 0, 'approved', '2024-02-01 10:00:00'),
            (1, 3, 10, 5, 'Perfect for artists', 'The pressure sensitivity is amazing. I can sketch just like on paper but with all the digital benefits.', 1, 32, 0, 'approved', '2024-04-10 15:30:00'),
            (1, 5, 19, 4, 'Great for students', 'Love it for taking lecture notes. OCR works really well. Only wish battery lasted longer.', 1, 28, 0, 'approved', '2024-06-05 09:15:00'),
            (1, 7, 6, 3, 'Good but pricey', 'Works as advertised but $299 is steep. Worth it if you write a lot.', 1, 15, 2, 'approved', '2024-08-12 14:00:00'),
            (1, 9, None, 5, 'Best purchase of 2024', 'I run a business and use this for all my meetings and brainstorming. The AI idea expansion is genius.', 1, 67, 0, 'approved', '2024-10-20 11:30:00'),
            (2, 1, 2, 4, 'Good replacement', 'Works just like the original. Delivered quickly.', 1, 8, 0, 'approved', '2024-03-05 16:45:00'),
            (2, 13, None, 5, 'Essential backup', 'Lost my original stylus, this one works perfectly. Keep an extra on hand!', 1, 12, 0, 'approved', '2024-12-15 10:20:00'),
        ]

        cursor.executemany('''
            INSERT INTO product_reviews (product_id, customer_id, order_id, rating, review_title, review_text, is_verified_purchase, helpful_count, reported_count, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', reviews_data)
        print(f"✓ Inserted {len(reviews_data)} product reviews!")

        # ==================== INSERT RETURNS ====================
        print("19. Inserting returns...")
        returns_data = [
            ('RET-20240725-0001', 6, 7, 1, 'Dead pixels on display', 'refund', 'completed', 1, 325.91, 'RETURN-LABEL-7890', '2024-07-23 10:00:00', '2024-07-23 12:00:00', '2024-07-25 09:00:00', '2024-07-28 14:00:00', 'Refund processed'),
            ('RET-20250113-0002', 36, 18, 1, 'Stylus tracking not working properly', 'exchange', 'completed', 1, 0.00, 'RETURN-LABEL-7891', '2025-01-13 14:00:00', '2025-01-13 15:00:00', '2025-01-15 10:00:00', '2025-01-16 12:00:00', 'Exchanged for new unit'),
        ]

        cursor.executemany('''
            INSERT INTO returns (return_number, order_id, customer_id, product_id, return_reason, return_type, return_status, quantity, refund_amount, return_shipping_label, requested_date, approved_date, received_date, completed_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', returns_data)
        print(f"✓ Inserted {len(returns_data)} returns!")

        # ==================== INSERT PROMOTIONS ====================
        print("20. Inserting promotions...")
        promotions_data = [
            ('STUDENT10', 'Student Discount', 'percentage', 10.0, 0.0, None, 'SSAI-NB-001', '2024-01-01', '2025-12-31', None, 15, 1),
            ('BULK5', 'Bulk Purchase Discount', 'percentage', 10.0, 500.0, None, 'ALL', '2024-01-01', '2025-12-31', None, 3, 1),
            ('WELCOME15', 'New Customer Welcome', 'percentage', 15.0, 0.0, 50.0, 'ALL', '2024-01-01', '2024-12-31', 500, 234, 0),
            ('STYLUS5OFF', 'Stylus Discount', 'fixed_amount', 5.0, 0.0, None, 'SSAI-STY-001', '2024-06-01', '2024-08-31', None, 89, 0),
        ]

        cursor.executemany('''
            INSERT INTO promotions (promotion_code, promotion_name, discount_type, discount_value, min_purchase_amount, max_discount_amount, applicable_products, start_date, end_date, usage_limit, usage_count, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', promotions_data)
        print(f"✓ Inserted {len(promotions_data)} promotions!")

        # Update customer totals
        print("\n21. Updating customer totals and loyalty points...")
        cursor.execute('''
            UPDATE customers
            SET total_purchases = (
                SELECT COALESCE(SUM(final_amount), 0)
                FROM orders
                WHERE orders.customer_id = customers.customer_id
                AND payment_status = 'paid'
                AND order_status NOT IN ('cancelled', 'refunded')
            ),
            loyalty_points = (
                SELECT COALESCE(CAST(SUM(final_amount) AS INTEGER), 0)
                FROM orders
                WHERE orders.customer_id = customers.customer_id
                AND payment_status = 'paid'
                AND order_status NOT IN ('cancelled', 'refunded')
            )
        ''')
        print("✓ Customer totals updated!")

        conn.commit()

        # ==================== VERIFICATION ====================
        print("\n" + "="*80)
        print("DATABASE VERIFICATION")
        print("="*80)

        tables = [
            'customers', 'products', 'orders', 'shipments', 'support_tickets',
            'ticket_messages', 'product_reviews', 'returns', 'promotions', 'inventory_logs'
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table:.<30} {count:>6} records")

        print("\nOrder Status Distribution:")
        cursor.execute('''
            SELECT order_status, COUNT(*) as count
            FROM orders
            GROUP BY order_status
            ORDER BY count DESC
        ''')
        for row in cursor.fetchall():
            print(f"  - {row[0]:.<20} {row[1]:>4}")

        print("\nSupport Ticket Status:")
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM support_tickets
            GROUP BY status
        ''')
        for row in cursor.fetchall():
            print(f"  - {row[0]:.<20} {row[1]:>4}")

        print("\nProduct Review Average Ratings:")
        cursor.execute('''
            SELECT p.product_name, COUNT(r.review_id) as review_count, AVG(r.rating) as avg_rating
            FROM products p
            LEFT JOIN product_reviews r ON p.product_id = r.product_id
            WHERE r.status = 'approved'
            GROUP BY p.product_id, p.product_name
        ''')
        for row in cursor.fetchall():
            if row[1] > 0:
                print(f"  - {row[0]:.<40} {row[1]:>3} reviews, {row[2]:.2f} stars")

        print("\n" + "="*80)
        print(f"✓ EXTENDED DATABASE SETUP COMPLETED!")
        print(f"✓ Database saved to: {full_db_path}")
        print("="*80)

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print("SmartScribble Extended SQLite Database Setup")
    print("="*80)
    print()

    success = setup_extended_database('smartscribble_extended.db')

    if success:
        print("\nDatabase created with the following tables:")
        print("  1. customers - Customer information")
        print("  2. products - Product catalog")
        print("  3. orders - Order records")
        print("  4. shipments - Shipping tracking")
        print("  5. support_tickets - Customer support tickets")
        print("  6. ticket_messages - Ticket conversation history")
        print("  7. product_reviews - Customer reviews and ratings")
        print("  8. returns - Return and exchange requests")
        print("  9. promotions - Discount codes and campaigns")
        print(" 10. inventory_logs - Stock movement tracking")
        print("\nYou can now integrate these tables with your customer support agent!")
