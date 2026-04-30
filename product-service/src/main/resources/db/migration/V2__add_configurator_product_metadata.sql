ALTER TABLE products ADD COLUMN component_type VARCHAR(32) NOT NULL DEFAULT 'OTHER';
ALTER TABLE products ADD COLUMN socket VARCHAR(40);
ALTER TABLE products ADD COLUMN supported_sockets VARCHAR(255);
ALTER TABLE products ADD COLUMN ram_type VARCHAR(20);
ALTER TABLE products ADD COLUMN gpu_tdp INTEGER NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN cpu_tdp INTEGER NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN psu_watts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN supports_wifi BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE products ADD COLUMN score_gaming NUMERIC(4, 2) NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN score_work NUMERIC(4, 2) NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN score_study NUMERIC(4, 2) NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN score_general NUMERIC(4, 2) NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN notes VARCHAR(1000);

UPDATE products
SET
    component_type = 'CPU',
    socket = 'AM5',
    cpu_tdp = 120,
    score_gaming = 9.40,
    score_work = 8.80,
    score_study = 8.20,
    score_general = 8.70,
    notes = 'Excellent gaming CPU,Strong AM5 upgrade path'
WHERE name = 'Ryzen 7 7800X3D';

UPDATE products
SET
    component_type = 'CPU',
    socket = 'LGA1700',
    cpu_tdp = 125,
    score_gaming = 8.90,
    score_work = 9.20,
    score_study = 8.10,
    score_general = 8.60,
    notes = 'Great multicore performance'
WHERE name = 'Core i7-14700K';

UPDATE products
SET
    component_type = 'GPU',
    gpu_tdp = 220,
    score_gaming = 9.10,
    score_work = 7.90,
    score_study = 6.80,
    score_general = 7.60,
    notes = 'Great for 1440p gaming'
WHERE name = 'GeForce RTX 4070 Super';

UPDATE products
SET
    component_type = 'GPU',
    gpu_tdp = 263,
    score_gaming = 8.90,
    score_work = 7.80,
    score_study = 6.70,
    score_general = 7.50,
    notes = 'High raster performance'
WHERE name = 'Radeon RX 7800 XT';

UPDATE products
SET
    component_type = 'RAM',
    ram_type = 'DDR5',
    score_gaming = 8.30,
    score_work = 8.50,
    score_study = 7.80,
    score_general = 8.00,
    notes = '32GB dual-channel kit'
WHERE name = 'DDR5 32GB Kit 6000MHz';

UPDATE products
SET
    price = 19000,
    currency = 'RUB'
WHERE name = 'Ryzen 7 7800X3D';

UPDATE products
SET
    price = 29000,
    currency = 'RUB'
WHERE name = 'Core i7-14700K';

UPDATE products
SET
    price = 62000,
    currency = 'RUB'
WHERE name = 'GeForce RTX 4070 Super';

UPDATE products
SET
    price = 56000,
    currency = 'RUB'
WHERE name = 'Radeon RX 7800 XT';

UPDATE products
SET
    price = 13000,
    currency = 'RUB'
WHERE name = 'DDR5 32GB Kit 6000MHz';

INSERT INTO categories(name, slug)
SELECT 'Motherboards', 'motherboards'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'motherboards');

INSERT INTO categories(name, slug)
SELECT 'Storage', 'storage'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'storage');

INSERT INTO categories(name, slug)
SELECT 'Power Supplies', 'power-supplies'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'power-supplies');

INSERT INTO categories(name, slug)
SELECT 'Cases', 'cases'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'cases');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ASUS TUF B650-PLUS WIFI',
    'AM5 ATX motherboard with DDR5 and Wi-Fi',
    'ASUS',
    22000,
    'RUB',
    TRUE,
    12,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'AM5',
    NULL,
    'DDR5',
    0,
    0,
    0,
    TRUE,
    8.50,
    8.40,
    8.10,
    8.30,
    'Reliable AM5 platform'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ASUS TUF B650-PLUS WIFI');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Gigabyte B760M DS3H',
    'LGA1700 micro-ATX motherboard with DDR4',
    'Gigabyte',
    15000,
    'RUB',
    TRUE,
    14,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'LGA1700',
    'Socket V',
    'DDR4',
    0,
    0,
    0,
    FALSE,
    7.80,
    7.80,
    7.50,
    7.60,
    'Affordable Intel platform board'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Gigabyte B760M DS3H');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'NVMe SSD 1TB PCIe 4.0',
    'Fast PCIe 4.0 SSD',
    'WD',
    7000,
    'RUB',
    TRUE,
    35,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    8.00,
    8.30,
    7.80,
    7.90,
    'Good value NVMe drive'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'NVMe SSD 1TB PCIe 4.0');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '650W 80+ Bronze PSU',
    'Entry-level reliable PSU',
    'DeepCool',
    5500,
    'RUB',
    TRUE,
    28,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    650,
    FALSE,
    7.40,
    7.40,
    7.20,
    7.30,
    'Enough for mid-range GPU builds'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '650W 80+ Bronze PSU');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ATX Mid Tower Airflow Case',
    'Airflow-focused ATX case',
    'Zalman',
    5000,
    'RUB',
    TRUE,
    24,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    7.50,
    7.50,
    7.50,
    7.50,
    'Good thermal performance for budget builds'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ATX Mid Tower Airflow Case');
