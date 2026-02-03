CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    available BOOLEAN DEFAULT true
);

INSERT INTO menu_items (name, description, price, category, available) VALUES
('Pizza', 'Delicious cheese pizza', 12.99, 'Main', true),
('Burger', 'Classic beef burger', 8.99, 'Main', true),
('Pasta', 'Creamy alfredo pasta', 10.99, 'Main', true),
('Salad', 'Fresh garden salad', 6.99, 'Appetizer', true),
('Soda', 'Refreshing soft drink', 2.99, 'Beverage', true);
