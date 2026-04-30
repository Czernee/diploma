-- Make existing key GPU available for wider mid/high range coverage.
UPDATE products
SET in_stock = TRUE, stock_quantity = 10
WHERE name = 'Radeon RX 7800 XT';

-- Budget CPUs
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Ryzen 5 5600',
    '6-core budget AM4 CPU',
    'AMD',
    11000,
    'RUB',
    TRUE,
    30,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'AM4',
    NULL,
    NULL,
    0,
    65,
    0,
    FALSE,
    7.60,
    7.20,
    7.10,
    7.30,
    'Great value gaming CPU'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Ryzen 5 5600');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Core i3-12100F',
    '4-core budget LGA1700 CPU',
    'Intel',
    9000,
    'RUB',
    TRUE,
    25,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'LGA1700',
    'Socket V',
    NULL,
    0,
    58,
    0,
    FALSE,
    6.90,
    6.80,
    7.00,
    6.90,
    'Entry desktop CPU'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Core i3-12100F');

-- High-end CPU
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Ryzen 9 7950X3D',
    '16-core flagship AM5 CPU',
    'AMD',
    62000,
    'RUB',
    TRUE,
    8,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'AM5',
    NULL,
    NULL,
    0,
    120,
    0,
    FALSE,
    9.80,
    9.70,
    9.20,
    9.50,
    'Top-tier gaming and productivity CPU'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Ryzen 9 7950X3D');

-- Budget / mid / high GPUs
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Radeon RX 6600',
    'Budget 1080p gaming GPU',
    'AMD',
    19000,
    'RUB',
    TRUE,
    18,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    132,
    0,
    0,
    FALSE,
    7.10,
    6.40,
    6.10,
    6.50,
    '8GB VRAM, efficient 1080p card'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Radeon RX 6600');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce RTX 4060',
    'Mainstream 1080p/1440p GPU',
    'NVIDIA',
    32000,
    'RUB',
    TRUE,
    14,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    115,
    0,
    0,
    FALSE,
    8.00,
    7.00,
    6.50,
    7.00,
    '8GB VRAM with DLSS support'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce RTX 4060');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce RTX 4090',
    'Flagship 4K gaming GPU',
    'NVIDIA',
    190000,
    'RUB',
    TRUE,
    4,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    450,
    0,
    0,
    FALSE,
    9.95,
    9.20,
    8.60,
    9.10,
    '24GB VRAM for extreme workloads'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce RTX 4090');

-- Motherboards for AM4 / AM5 / LGA1700 spread
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'MSI B450M PRO-VDH MAX',
    'Budget AM4 motherboard with DDR4',
    'MSI',
    7500,
    'RUB',
    TRUE,
    20,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'AM4',
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    6.90,
    6.90,
    6.80,
    6.90,
    'Entry AM4 board'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'MSI B450M PRO-VDH MAX');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ASUS ROG STRIX X670E-E GAMING WIFI',
    'Premium AM5 motherboard',
    'ASUS',
    42000,
    'RUB',
    TRUE,
    5,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'AM5',
    NULL,
    'DDR5',
    0,
    0,
    0,
    TRUE,
    9.20,
    9.10,
    8.70,
    9.00,
    'High-end AM5 board with robust VRM'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ASUS ROG STRIX X670E-E GAMING WIFI');

-- RAM options
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '16GB DDR4 3200',
    '2x8GB DDR4 memory kit',
    'Kingston',
    4500,
    'RUB',
    TRUE,
    40,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    7.10,
    7.20,
    7.40,
    7.20,
    '16GB dual-channel kit'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '16GB DDR4 3200');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '64GB DDR5 6000',
    '2x32GB DDR5 high capacity kit',
    'G.Skill',
    24000,
    'RUB',
    TRUE,
    9,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR5',
    0,
    0,
    0,
    FALSE,
    9.00,
    9.30,
    8.80,
    9.00,
    '64GB dual-channel kit'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '64GB DDR5 6000');

-- Storage options
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'NVMe SSD 512GB PCIe 3.0',
    'Affordable SSD for budget builds',
    'Kingston',
    3500,
    'RUB',
    TRUE,
    50,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    7.00,
    7.20,
    7.20,
    7.10,
    'Budget 512GB SSD'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'NVMe SSD 512GB PCIe 3.0');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'NVMe SSD 2TB PCIe 4.0',
    'High-capacity PCIe 4.0 SSD',
    'Samsung',
    14500,
    'RUB',
    TRUE,
    20,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    8.90,
    9.10,
    8.70,
    8.90,
    'Fast 2TB storage'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'NVMe SSD 2TB PCIe 4.0');

-- PSU options
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '550W 80+ Bronze PSU',
    'Budget PSU for entry gaming builds',
    'DeepCool',
    3900,
    'RUB',
    TRUE,
    30,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    550,
    FALSE,
    6.90,
    7.00,
    7.00,
    6.90,
    'Entry 550W unit'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '550W 80+ Bronze PSU');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '1000W 80+ Gold PSU',
    'High-end PSU for flagship GPUs',
    'Corsair',
    18000,
    'RUB',
    TRUE,
    10,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    1000,
    FALSE,
    9.20,
    9.20,
    8.80,
    9.00,
    'Stable 1000W output for high-end systems'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '1000W 80+ Gold PSU');

-- Cases
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'mATX Compact Case',
    'Budget compact airflow case',
    'AeroCool',
    3200,
    'RUB',
    TRUE,
    30,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    6.80,
    6.90,
    7.10,
    6.90,
    'Compact budget case'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'mATX Compact Case');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Premium Full Tower Airflow Case',
    'High-end full tower for flagship builds',
    'Lian Li',
    14500,
    'RUB',
    TRUE,
    8,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    9.00,
    8.90,
    8.50,
    8.80,
    'Large chassis with top airflow'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Premium Full Tower Airflow Case');
