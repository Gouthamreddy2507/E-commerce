from flask import Flask, render_template, redirect, url_for, request, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import random
from database import db
from datetime import datetime, timedelta
import razorpay
import bcrypt
import mysql.connector
import venv


app = Flask(__name__)
app.secret_key = 'simplelogin'

RAZORPAY_KEY_ID = "rzp_test_xxfkdUYWCKHS4E"
RAZORPAY_KEY_SECRET = "DDFK36eIKqNL514rmiJ4vahF"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tummalasowmya2018@gmail.com'
app.config['MAIL_PASSWORD'] = 'pzfm niqj xkpc xsgc'
app.config['MAIL_DEFAULT_SENDER'] = 'tummalasowmya2018@gmail.com'

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(name, email, otp):
    try:
        msg = Message('OTP for Verification', recipients=[email])
        msg.body = f"Hello {name}!\nYour OTP is: {otp}"
        mail.send(msg)
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False


@app.route('/myorders')
def myorders():
    return render_template('myorders.html')

@app.route('/mycarts')
def mycarts():
    return render_template('mycarts.html')

@app.route('/')
def dashboard():
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))

    # user_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    # Fetch all products
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Fetch user's favorite product IDs
    # cursor.execute("SELECT product_id FROM favorites WHERE user_id = %s", (user_id,))
    # favorite_rows = cursor.fetchall()
    # favorite_ids = [row['product_id'] for row in favorite_rows]

    return render_template('dashboard.html', products=products)




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phoneno = request.form.get('phoneno')
        gender = request.form.get('gender')

        if not all([username, email, password, phoneno, gender]):
            error = "All fields are required."
            return render_template('register.html', error=error)

        if not phoneno.isdigit() or len(phoneno) != 10:
            error = "Phone number must be 10 digits."
            return render_template('register.html', error=error)

        if gender not in ['Male', 'Female', 'other']:
            error = "Invalid gender selected."
            return render_template('register.html', error=error)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
        if cursor.fetchone():
            error = "Email is already registered."
            return render_template('register.html', error=error)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute("""
            INSERT INTO user_data (username, email, password, phoneno, gender)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, email, hashed_password, phoneno, gender))
        db.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('login.html', error='Please enter both email and password.')

        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM user_data WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            otp = generate_otp()
            session['otp'] = otp

            if send_otp_email(user[1], email, otp):
                return redirect(url_for('verify'))
            else:
                return render_template('login.html', error='Failed to send OTP. Please try again later.')

        return render_template('login.html', error='Incorrect email or password.')

    return render_template('login.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    error = request.args.get('error')

    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if 'otp' in session and session['otp'] == entered_otp:
            del session['otp']
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('verify', error="Invalid OTP, please try again."))

    return render_template('verify.html', error=error)


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    message = None
    message_type = "error"  

    if request.method == 'POST':
        email = request.form.get('email')

        cursor = db.cursor()
        cursor.execute("SELECT id FROM user_data WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('resetpassword', token=token, _external=True)

            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f'Click the link to reset your password: {reset_url}\n\nThis link will expire in 1 hour.'
            mail.send(msg)

            message = "A password reset link has been sent to your email."
            message_type = "success"
        else:
            message = "No account found with this email."

    return render_template('forgotpassword.html', message=message, message_type=message_type)


@app.route('/resetpassword/<token>', methods=['GET', 'POST'])
def resetpassword(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires in 1 hour
    except SignatureExpired:
        return render_template('resetpassword.html', message="Token expired. Request a new link.", message_type="error")

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('resetpassword.html', email=email, message="Passwords do not match!", message_type="error")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = db.cursor()
        cursor.execute("UPDATE user_data SET password=%s WHERE email=%s", (hashed_password, email))
        db.commit()

        return redirect(url_for('login', message="Password successfully reset. You can now log in.", message_type="success"))

    return render_template('resetpassword.html', email=email)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/add_favorite/<int:product_id>')
def add_favorite(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor = db.cursor()
    uid = session['user_id']
    cursor.execute("SELECT id FROM favorites WHERE user_id=%s AND product_id=%s", (uid, product_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO favorites (user_id, product_id) VALUES (%s,%s)", (uid, product_id))
        db.commit()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/remove_favorite/<int:product_id>')
def remove_favorite(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor = db.cursor()
    cursor.execute("DELETE FROM favorites WHERE user_id=%s AND product_id=%s", (session['user_id'], product_id))
    db.commit()
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    uid = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.* FROM favorites f 
        JOIN products p ON f.product_id = p.id
        WHERE f.user_id = %s
    """, (uid,))
    favs = cursor.fetchall()
    return render_template('favorites.html', favorites=favs)


@app.route('/product/<int:product_id>/add_review', methods=['POST'])
def add_review(product_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session.get('user_id')  # Make sure the user is logged in

    if not rating or not comment:
        error = "All fields are required."
        return redirect(url_for('product_detail', product_id=product_id, error=error))

    try:
        rating = float(rating)
        if not (0.5 <= rating <= 5.0):
            raise ValueError
    except ValueError:
        error = "Rating must be between 0.5 and 5.0"
        return redirect(url_for('product_detail', product_id=product_id, error=error))

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO product_comments (product_id, user_id, comment, rating)
        VALUES (%s, %s, %s, %s)
    """, (product_id, user_id, comment, rating))
    db.commit()
    cursor.close()

    return redirect(url_for('product_detail', product_id=product_id))




@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cursor = db.cursor(dictionary=True)

    # Get product
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    # Get reviews
    cursor.execute("""
    SELECT pc.*, u.username 
    FROM product_comments pc
    LEFT JOIN user_data u ON pc.user_id = u.id
    WHERE pc.product_id = %s
    ORDER BY pc.created_at DESC
""", (product_id,))

    product_comments = cursor.fetchall()

    # Get favorites if user is logged in
    favorite_ids = []
    user_id = session.get('user_id')
    if user_id:
        cursor.execute("SELECT product_id FROM favorites WHERE user_id = %s", (user_id,))
        favorite_ids = [row['product_id'] for row in cursor.fetchall()]

    cursor.close()
    return render_template('product_detail.html', product=product, product_comments=product_comments, favorite_ids=favorite_ids)




@app.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
def checkout(product_id):
    cursor = db.cursor(dictionary=True)

    # ✅ 1. Fetch product details
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    # ✅ 2. Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # ✅ 3. Fetch user's saved address
    cursor.execute("SELECT address, city, state, pin FROM user_data WHERE id = %s", (user_id,))
    saved_address = cursor.fetchone()

    if request.method == 'POST':
        # ✅ 4. Get address from form
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        pin = request.form['pin']

        full_address = f"{address}, {city}, {state}, {pin}"
        order_date = datetime.now()
        delivery_date = order_date + timedelta(days=5)

        # ✅ 5. Update user_data if address changed or new
        cursor.execute("""
            UPDATE user_data
            SET address = %s, city = %s, state = %s, pin = %s
            WHERE id = %s
        """, (address, city, state, pin, user_id))

        # ✅ 6. Insert order into orders table
        cursor.execute("""
            INSERT INTO orders (
                user_id, product_id, quantity, total_price, address,
                order_date, delivery_date, status, payment_mode
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            product_id,
            1,  # default quantity
            product['price'],
            full_address,
            order_date,
            delivery_date,
            'Processing',
            'Pending'
        ))

        db.commit()
        order_id = cursor.lastrowid
        cursor.close()

        return redirect(url_for('order_summary', order_id=order_id))

    # ✅ Render checkout page (prefill address if available)
    return render_template(
        'checkout.html',
        product=product,
        user_address=saved_address
    )



@app.route('/order_summary/<int:order_id>')
def order_summary(order_id):
    cursor = db.cursor(dictionary=True)
    
    # Fetch the order details
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        return redirect(url_for('home'))
    
    # Fetch the product details associated with the order
    cursor.execute("SELECT * FROM products WHERE id = %s", (order['product_id'],))
    product = cursor.fetchone()

    print("*************",order,product)
    
    cursor.close()

    return render_template('order_summary.html', order=order, product=product)



@app.route('/payment/<int:order_id>')
def payment(order_id):
    # Fetch order from database
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        return "Order not found", 404

    # Fetch product details for this order
    cursor.execute("SELECT * FROM products WHERE id = %s", (order['product_id'],))
    product = cursor.fetchone()
    
    cursor.close()

    if not product:
        return "Product not found", 404

    amount = int(product['price']) * 100  # Razorpay expects amount in paise (INR)

    # Create a Razorpay order
    razorpay_order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    print(razorpay_order,'razorpay_order**************')

    # Store Razorpay Order ID in session or DB (optional)
    order['razorpay_order_id'] = razorpay_order['id']

    return render_template('payment.html', order=order, product=product, razorpay_order_id=razorpay_order['id'], razorpay_key=RAZORPAY_KEY_ID)


@app.route('/payment_success/<int:order_id>', methods=['POST'])
def payment_success(order_id):
    cursor = db.cursor(dictionary=True)

    # Fetch the order from the database
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        return "Order not found", 404

    # Fetch product details for the order
    cursor.execute("SELECT * FROM products WHERE id = %s", (order['product_id'],))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    payment_id = request.form.get("razorpay_payment_id")
    razorpay_order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")

    print("Received Payment ID:", payment_id)
    print("Received Order ID:", razorpay_order_id)
    print("Received Signature:", signature)

    if not payment_id or not razorpay_order_id or not signature:
        return "Missing payment details", 400

    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
        cursor.execute(
            """
            UPDATE orders 
            SET status = %s, payment_status = %s, payment_mode = %s
            WHERE id = %s
            """, 
            ("Processing", "Completed", "Razorpay", order_id)
        )

        cursor.close()

        return render_template('payment_success.html', order=order, product=product)
    
    except razorpay.errors.SignatureVerificationError:
        return "Payment verification failed", 400

    



@app.route('/add_cart', methods=['GET'])
def add_cart(product_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor = db.cursor()
    uid = session['user_id']
    pid = product_id or request.args.get('product_id', type=int)
    qty = request.form.get('quantity', 1, type=int)
    # If existing, increment quantity
    cursor.execute("SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s", (uid, pid))
    item = cursor.fetchone()
    if item:
        cursor.execute("UPDATE cart SET quantity=quantity+%s WHERE id=%s", (qty, item[0]))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,%s)", (uid, pid, qty))
    db.commit()
    return redirect(request.referrer or url_for('show_cart'))

@app.route('/cart')
def show_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    uid = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id AS cart_id, p.*, c.quantity, (p.price * c.quantity) AS subtotal
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (uid,))
    items = cursor.fetchall()
    total = sum(item['subtotal'] for item in items)
    return render_template('cart.html', cart_items=items, total=total)





@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    uid = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, p.name AS product_name, p.image AS product_img
        FROM orders o JOIN products p ON o.product_id = p.id
        WHERE o.user_id = %s ORDER BY o.order_date DESC
    """, (uid,))
    orders = cursor.fetchall()
    return render_template('my_orders.html', orders=orders)



@app.route('/about')
def about():

    return redirect(url_for('dashboard'))

@app.route('/contact')
def contact():

    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(debug=True)

