-- Budget CPUs
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Ryzen 5 5600',
    '6-core AM4 processor for affordable gaming and study builds',
    'AMD',
    9000,
    'RUB',
    TRUE,
    35,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'AM4',
    NULL,
    NULL,
    0,
    65,
    0,
    FALSE,
    7.80,
    7.40,
    7.50,
    7.50,
    'Budget CPU,Good value in 2026'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Ryzen 5 5600');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Core i5-13400F',
    '10-core LGA1700 processor for mixed workloads',
    'Intel',
    16500,
    'RUB',
    TRUE,
    26,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'LGA1700',
    NULL,
    NULL,
    0,
    65,
    0,
    FALSE,
    8.10,
    8.20,
    7.90,
    8.00,
    'Strong mid-range CPU,Low power draw'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Core i5-13400F');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Ryzen 9 7900X',
    '12-core AM5 processor for heavy creator and work scenarios',
    'AMD',
    32000,
    'RUB',
    TRUE,
    14,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'AM5',
    NULL,
    NULL,
    0,
    170,
    0,
    FALSE,
    9.00,
    9.40,
    8.60,
    8.90,
    'High multicore performance,Needs good cooling'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Ryzen 9 7900X');

-- GPUs for low/mid/high budgets
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce RTX 3050 8GB',
    'Entry gaming GPU for 1080p builds',
    'NVIDIA',
    19000,
    'RUB',
    TRUE,
    22,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    130,
    0,
    0,
    FALSE,
    7.20,
    6.90,
    6.70,
    6.90,
    '8GB VRAM,Good entry option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce RTX 3050 8GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce RTX 4060 8GB',
    'Efficient 1080p/1440p graphics card',
    'NVIDIA',
    29000,
    'RUB',
    TRUE,
    20,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    115,
    0,
    0,
    FALSE,
    8.10,
    7.30,
    7.10,
    7.50,
    '8GB VRAM,DLSS support'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce RTX 4060 8GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Radeon RX 7600 8GB',
    'Affordable raster-focused 1080p GPU',
    'AMD',
    25000,
    'RUB',
    TRUE,
    18,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    165,
    0,
    0,
    FALSE,
    7.90,
    7.10,
    6.80,
    7.20,
    '8GB VRAM,Strong value in budget builds'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Radeon RX 7600 8GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce RTX 4080 Super 16GB',
    'High-end 4K GPU with strong ray tracing',
    'NVIDIA',
    110000,
    'RUB',
    TRUE,
    7,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    320,
    0,
    0,
    FALSE,
    9.70,
    8.70,
    7.80,
    8.80,
    '16GB VRAM,Top tier gaming'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce RTX 4080 Super 16GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Radeon RX 7900 XTX 24GB',
    'Flagship AMD GPU for high resolution workloads',
    'AMD',
    98000,
    'RUB',
    TRUE,
    8,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    355,
    0,
    0,
    FALSE,
    9.50,
    8.60,
    7.70,
    8.70,
    '24GB VRAM,Excellent raster performance'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Radeon RX 7900 XTX 24GB');

UPDATE products
SET in_stock = TRUE, stock_quantity = 9
WHERE name = 'Radeon RX 7800 XT';

-- Motherboards
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'MSI B550M PRO-VDH WIFI',
    'AM4 micro-ATX motherboard with onboard Wi-Fi',
    'MSI',
    9800,
    'RUB',
    TRUE,
    24,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'AM4',
    NULL,
    'DDR4',
    0,
    0,
    0,
    TRUE,
    7.60,
    7.70,
    7.70,
    7.70,
    'Budget AM4 board,Wi-Fi included'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'MSI B550M PRO-VDH WIFI');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ASRock B650M-HDV/M.2',
    'Affordable AM5 DDR5 motherboard for entry AM5 builds',
    'ASRock',
    13500,
    'RUB',
    TRUE,
    16,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'AM5',
    NULL,
    'DDR5',
    0,
    0,
    0,
    FALSE,
    7.90,
    7.90,
    7.70,
    7.80,
    'AM5 platform,Good budget option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ASRock B650M-HDV/M.2');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'MSI PRO Z790-P WIFI',
    'LGA1700 ATX DDR5 board for high-end Intel builds',
    'MSI',
    28500,
    'RUB',
    TRUE,
    10,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'LGA1700',
    'Socket V',
    'DDR5',
    0,
    0,
    0,
    TRUE,
    8.90,
    9.00,
    8.20,
    8.60,
    'High-end VRM,Wi-Fi 6 support'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'MSI PRO Z790-P WIFI');

-- RAM kits
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'DDR4 16GB Kit 3200MHz',
    '2x8GB DDR4 memory kit',
    'Kingston',
    4200,
    'RUB',
    TRUE,
    48,
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
    6.90,
    7.20,
    7.00,
    '16GB total,Good for entry builds'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'DDR4 16GB Kit 3200MHz');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'DDR4 32GB Kit 3600MHz',
    '2x16GB DDR4 memory kit for multitasking and work',
    'Corsair',
    7600,
    'RUB',
    TRUE,
    30,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    8.10,
    8.20,
    7.80,
    7.90,
    '32GB total,Excellent value'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'DDR4 32GB Kit 3600MHz');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'DDR5 16GB Kit 5600MHz',
    '2x8GB DDR5 starter kit',
    'ADATA',
    5600,
    'RUB',
    TRUE,
    34,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR5',
    0,
    0,
    0,
    FALSE,
    7.40,
    7.20,
    7.40,
    7.30,
    '16GB total,Entry DDR5 option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'DDR5 16GB Kit 5600MHz');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'DDR5 64GB Kit 6000MHz',
    '2x32GB DDR5 kit for advanced work and creator tasks',
    'G.Skill',
    22000,
    'RUB',
    TRUE,
    12,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR5',
    0,
    0,
    0,
    FALSE,
    8.80,
    9.40,
    8.60,
    8.90,
    '64GB total,High capacity DDR5'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'DDR5 64GB Kit 6000MHz');

-- Storage
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'SATA SSD 1TB',
    'Affordable 1TB SATA SSD',
    'Crucial',
    4500,
    'RUB',
    TRUE,
    60,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    6.80,
    6.90,
    7.20,
    6.90,
    'Low price storage option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'SATA SSD 1TB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'NVMe SSD 512GB PCIe 4.0',
    'Fast boot drive for budget systems',
    'Kingston',
    3900,
    'RUB',
    TRUE,
    55,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    7.20,
    7.20,
    7.30,
    7.20,
    'Small but fast,good for OS and apps'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'NVMe SSD 512GB PCIe 4.0');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'NVMe SSD 2TB PCIe 4.0',
    'High capacity and speed for games and projects',
    'Samsung',
    12500,
    'RUB',
    TRUE,
    22,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    8.70,
    9.10,
    8.20,
    8.60,
    '2TB capacity,Fast sustained throughput'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'NVMe SSD 2TB PCIe 4.0');

-- PSUs
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '550W 80+ Bronze PSU',
    'Affordable PSU for entry and mainstream builds',
    'Chieftec',
    4300,
    'RUB',
    TRUE,
    38,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    550,
    FALSE,
    7.00,
    7.00,
    7.10,
    7.00,
    'Good for up to mid-range GPUs'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '550W 80+ Bronze PSU');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '750W 80+ Gold PSU',
    'High efficiency PSU for powerful systems',
    'Seasonic',
    10900,
    'RUB',
    TRUE,
    20,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    750,
    FALSE,
    8.60,
    8.70,
    8.00,
    8.40,
    'Recommended for high-end GPUs'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '750W 80+ Gold PSU');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '850W 80+ Gold PSU',
    'High-headroom PSU for flagship GPUs',
    'Corsair',
    13900,
    'RUB',
    TRUE,
    14,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    850,
    FALSE,
    8.90,
    9.00,
    8.20,
    8.70,
    'Headroom for 320W+ GPUs'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '850W 80+ Gold PSU');

-- Cases
INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Compact mATX Mesh Case',
    'Budget airflow-focused micro-ATX case',
    'AeroCool',
    3600,
    'RUB',
    TRUE,
    32,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    7.10,
    7.10,
    7.20,
    7.10,
    'Affordable airflow case'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Compact mATX Mesh Case');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ATX Mid Tower RGB Case',
    'Mid-range ATX case with mesh front and RGB fans',
    'DeepCool',
    6900,
    'RUB',
    TRUE,
    21,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    8.00,
    8.00,
    7.90,
    8.00,
    'Balanced thermals and acoustics'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ATX Mid Tower RGB Case');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Premium Airflow Full Tower Case',
    'Large chassis for high-end systems and custom cooling',
    'Fractal Design',
    14500,
    'RUB',
    TRUE,
    9,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    8.90,
    8.90,
    8.30,
    8.70,
    'Excellent cable management and airflow'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Premium Airflow Full Tower Case');
