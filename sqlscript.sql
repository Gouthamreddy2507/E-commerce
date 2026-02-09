
CREATE DATABASE ecommerce;
USE ecommerce;

show tables;

-- Users Table
-- Stores user information including login credentials and account creation date
CREATE TABLE user_data(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phoneno varchar(10) NOT NULL,
    gender ENUM('Female','Male','other') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_data
ADD COLUMN address TEXT,
ADD COLUMN city VARCHAR(100),
ADD COLUMN state VARCHAR(100),
ADD COLUMN pin VARCHAR(10);


select * from user_data;

-- Products Table
-- Contains product details including price, quantity, quality, discount, and seller status
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    quality ENUM('New', 'Used', 'Refurbished') DEFAULT 'New',
    discount DECIMAL(5,2) DEFAULT 0.00,
    best_seller BOOLEAN DEFAULT FALSE,
    image VARCHAR(255),
    rating DECIMAL(3,2),                  
    category VARCHAR(100),               
    return_policy TEXT,                 
    brand VARCHAR(100),                 
    status ENUM('active', 'out_of_stock', 'discontinued') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



select * from products;


CREATE TABLE product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    size VARCHAR(50),
    color VARCHAR(50),
    quantity INT NOT NULL,
    price DECIMAL(10,2),
    image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

select * from product_variants;


CREATE TABLE product_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT,
    comment TEXT NOT NULL,
    rating DECIMAL(2,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    -- Add FOREIGN KEY (user_id) if you have a users table
);



select * from product_comments;


-- Insert Product Data
-- Sample product data including electronics, accessories, and gadgets
INSERT INTO products (name, description, price, quantity, quality, discount, best_seller, image, rating, category, return_policy, brand, status)
VALUES
('Laptop', 'A high-performance laptop with the latest processor and 16GB RAM.', 1000.00, 10, 'New', 10.00, TRUE, 'static/images/laptop.png', 4.5, 'Electronics', '15-day return policy', 'TechBrand', 'active'),
('Smartphone', 'A latest-gen smartphone with AI camera and 5G connectivity.', 700.00, 20, 'New', 5.00, FALSE, 'static/images/smartphone.jpg', 4.3, 'Electronics', '10-day return policy', 'SmartX', 'active'),
('Headphones', 'Noise-cancelling headphones with immersive sound experience.', 150.00, 50, 'New', 15.00, TRUE, 'static/images/headphones.jpg', 4.6, 'Audio', '7-day return policy', 'SoundMax', 'active'),
('Smartwatch', 'A feature-rich smartwatch with health tracking and notifications.', 250.00, 30, 'New', 8.00, FALSE, 'static/images/smartwatch.jpg', 4.2, 'Wearables', '10-day return policy', 'WristTech', 'active'),
('Tablet', 'A powerful tablet with 10-inch display and stylus support.', 500.00, 15, 'New', 12.00, FALSE, 'static/images/tablet.jpg', 4.4, 'Electronics', '15-day return policy', 'TabPro', 'active'),
('Gaming Console', 'Next-gen gaming console with ultra HD graphics.', 600.00, 10, 'New', 7.00, TRUE, 'static/images/console.jpg', 4.7, 'Gaming', '15-day return policy', 'GameZone', 'active'),
('Wireless Earbuds', 'Compact earbuds with noise cancellation and long battery life.', 120.00, 40, 'New', 10.00, TRUE, 'static/images/earbuds.jpg', 4.3, 'Audio', '7-day return policy', 'EarPro', 'active'),
('Camera', 'Professional-grade DSLR camera with 4K video recording.', 1200.00, 5, 'New', 5.00, FALSE, 'static/images/camera.jpg', 4.6, 'Photography', '15-day return policy', 'PhotoPro', 'active'),
('Monitor', '4K Ultra HD monitor with high refresh rate for gaming.', 300.00, 25, 'New', 10.00, TRUE, 'static/images/monitor.jpg', 4.4, 'Electronics', '10-day return policy', 'ViewMax', 'active'),
('Keyboard', 'Mechanical keyboard with RGB lighting and fast response keys.', 80.00, 100, 'New', 5.00, FALSE, 'static/images/keyboard.jpg', 4.2, 'Peripherals', '7-day return policy', 'KeyTech', 'active');


-- Assume the product IDs are from 1 to 10 based on insert order

-- Laptop (Product ID 1)
INSERT INTO product_variants (product_id, size, color, quantity, price, image) VALUES
(1, '15-inch', 'Silver', 5, 1000.00, 'static/images/laptop.png'),
(1, '15-inch', 'Black', 5, 1000.00, 'static/images/laptop.png');

-- Smartphone (Product ID 2)
INSERT INTO product_variants (product_id, size, color, quantity, price, image) VALUES
(2, '128GB', 'Black', 10, 700.00, 'static/images/smartphone.jpg'),
(2, '256GB', 'Blue', 10, 750.00, 'static/images/smartphone.jpg');

-- Headphones (Product ID 3)
INSERT INTO product_variants (product_id, size, color, quantity, price, image) VALUES
(3, 'Standard', 'Black', 25, 150.00, 'static/images/headphones.jpg'),
(3, 'Standard', 'White', 25, 150.00, 'static/images/headphones.jpg');

-- Wireless Earbuds (Product ID 7)
INSERT INTO product_variants (product_id, size, color, quantity, price, image) VALUES
(7, 'One Size', 'Black', 20, 120.00, 'static/images/earbuds.jpg'),
(7, 'One Size', 'White', 20, 120.00, 'static/images/earbuds.jpg');


-- Reviews for Product ID 1 (Laptop)
INSERT INTO product_comments (product_id, user_id, comment, rating) VALUES
(1, 1, 'Great performance and battery life.', 4.5),
(1, 2, 'Could be lighter, but works great.', 4.0);

-- Reviews for Product ID 2 (Smartphone)
INSERT INTO product_comments (product_id, user_id, comment, rating) VALUES
(2, 3, 'Amazing camera and smooth UI.', 4.8);

-- Reviews for Product ID 3 (Headphones)
INSERT INTO product_comments (product_id, user_id, comment, rating) VALUES
(3, 4, 'Sound quality is fantastic.', 4.7);



CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_data(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

show tables;


CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    address TEXT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_date TIMESTAMP,
    status ENUM('Processing', 'Shipped', 'Out for Delivery', 'Delivered', 'Returned', 'Cancelled') DEFAULT 'Processing',
    payment_mode VARCHAR(50),
    payment_status ENUM('Pending', 'Completed', 'Failed', 'Refunded') DEFAULT 'Pending',
    tracking_id VARCHAR(50) UNIQUE,
    shipped_date TIMESTAMP NULL DEFAULT NULL,
    delivered_date TIMESTAMP NULL DEFAULT NULL,
    return_request BOOLEAN DEFAULT FALSE,
    return_reason TEXT DEFAULT NULL,
    order_notes TEXT DEFAULT NULL,
    coupon_code VARCHAR(50) DEFAULT NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_data(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

select * from orders;

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,b  
    product_id INT NOT NULL,
    variant_id INT,
    quantity INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_data(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    status ENUM('Pending', 'Completed', 'Failed', 'Refunded') DEFAULT 'Pending',
    transaction_id VARCHAR(100) UNIQUE,
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user_data(id) ON DELETE CASCADE
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id)
);
CREATE TABLE shipping_providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_info TEXT,
    tracking_url_template TEXT
);


