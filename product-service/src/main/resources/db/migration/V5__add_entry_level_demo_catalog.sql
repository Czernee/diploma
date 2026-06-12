-- Extra entry-level assortment for demo scenarios and low-budget configurator checks.
-- The configurator still validates socket, RAM type and PSU wattage before returning a build.

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Athlon 3000G',
    'Very affordable AM4 processor for office and study PCs',
    'AMD',
    3500,
    'RUB',
    TRUE,
    40,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'AM4',
    NULL,
    NULL,
    0,
    35,
    0,
    FALSE,
    4.20,
    5.30,
    5.50,
    5.10,
    'Entry desktop CPU,Low power draw'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Athlon 3000G');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Ryzen 3 4100',
    'Budget 4-core AM4 processor for basic home PCs',
    'AMD',
    5500,
    'RUB',
    TRUE,
    34,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'AM4',
    NULL,
    NULL,
    0,
    65,
    0,
    FALSE,
    6.20,
    6.20,
    6.30,
    6.20,
    'Budget CPU,Good for entry builds'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Ryzen 3 4100');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Core i3-10100F',
    'Low-cost 4-core LGA1200 processor for office and study systems',
    'Intel',
    5200,
    'RUB',
    TRUE,
    28,
    (SELECT id FROM categories WHERE slug = 'processors'),
    'CPU',
    'LGA1200',
    NULL,
    NULL,
    0,
    65,
    0,
    FALSE,
    6.00,
    6.10,
    6.20,
    6.10,
    'Entry desktop CPU,Affordable Intel platform'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Core i3-10100F');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce GT 1030 2GB',
    'Basic low-power GPU for office displays and very light games',
    'NVIDIA',
    6500,
    'RUB',
    TRUE,
    26,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    30,
    0,
    0,
    FALSE,
    3.60,
    4.80,
    5.00,
    4.70,
    '2GB VRAM,Low power draw'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce GT 1030 2GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Radeon RX 6400 4GB',
    'Compact entry GPU for inexpensive 1080p esports builds',
    'AMD',
    9000,
    'RUB',
    TRUE,
    24,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    53,
    0,
    0,
    FALSE,
    5.90,
    5.70,
    5.60,
    5.70,
    '4GB VRAM,Entry 1080p option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Radeon RX 6400 4GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'GeForce GTX 1650 4GB',
    'Affordable 1080p GPU for budget gaming',
    'NVIDIA',
    12000,
    'RUB',
    TRUE,
    18,
    (SELECT id FROM categories WHERE slug = 'graphics-cards'),
    'GPU',
    NULL,
    NULL,
    NULL,
    75,
    0,
    0,
    FALSE,
    6.70,
    6.20,
    6.10,
    6.30,
    '4GB VRAM,Good entry option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'GeForce GTX 1650 4GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ASRock A320M-HDV R4.0',
    'Very affordable AM4 DDR4 motherboard',
    'ASRock',
    4200,
    'RUB',
    TRUE,
    35,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'AM4',
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    5.60,
    5.90,
    6.10,
    5.90,
    'Entry AM4 board'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ASRock A320M-HDV R4.0');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'MSI H510M-A PRO',
    'Budget LGA1200 DDR4 motherboard',
    'MSI',
    5200,
    'RUB',
    TRUE,
    22,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'LGA1200',
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    5.80,
    6.00,
    6.10,
    6.00,
    'Affordable Intel platform board'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'MSI H510M-A PRO');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'ASUS PRIME H610M-K D4',
    'Entry LGA1700 DDR4 motherboard',
    'ASUS',
    6500,
    'RUB',
    TRUE,
    24,
    (SELECT id FROM categories WHERE slug = 'motherboards'),
    'MOTHERBOARD',
    'LGA1700',
    'Socket V',
    'DDR4',
    0,
    0,
    0,
    FALSE,
    6.20,
    6.30,
    6.30,
    6.30,
    'Affordable Intel platform board'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'ASUS PRIME H610M-K D4');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'DDR4 8GB 2666MHz',
    'Single 8GB DDR4 stick for very cheap PCs',
    'Patriot',
    1600,
    'RUB',
    TRUE,
    70,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    4.80,
    5.40,
    5.80,
    5.50,
    '8GB total,Lowest price RAM'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'DDR4 8GB 2666MHz');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'DDR4 16GB Kit 3000MHz',
    'Affordable 2x8GB DDR4 kit',
    'Patriot',
    3200,
    'RUB',
    TRUE,
    52,
    (SELECT id FROM categories WHERE slug = 'memory'),
    'RAM',
    NULL,
    NULL,
    'DDR4',
    0,
    0,
    0,
    FALSE,
    6.70,
    6.80,
    6.90,
    6.80,
    '16GB total,Good for entry builds'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'DDR4 16GB Kit 3000MHz');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'SATA SSD 240GB',
    'Small SSD for the cheapest boot drive',
    'Kingston',
    1400,
    'RUB',
    TRUE,
    80,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    4.80,
    5.30,
    5.40,
    5.30,
    'Budget 240GB SSD,Good for OS and apps'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'SATA SSD 240GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'SATA SSD 480GB',
    'Cheap SSD with enough room for basic work',
    'ADATA',
    2200,
    'RUB',
    TRUE,
    72,
    (SELECT id FROM categories WHERE slug = 'storage'),
    'STORAGE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    5.80,
    6.20,
    6.30,
    6.20,
    'Budget 480GB SSD,Low price storage option'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'SATA SSD 480GB');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '400W 80+ White PSU',
    'Very affordable PSU for low-power office PCs',
    'AeroCool',
    2300,
    'RUB',
    TRUE,
    44,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    400,
    FALSE,
    5.20,
    5.60,
    5.70,
    5.60,
    'Entry 400W unit,Low price'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '400W 80+ White PSU');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    '450W 80+ Bronze PSU',
    'Budget PSU with a little more headroom',
    'DeepCool',
    2700,
    'RUB',
    TRUE,
    39,
    (SELECT id FROM categories WHERE slug = 'power-supplies'),
    'PSU',
    NULL,
    NULL,
    NULL,
    0,
    0,
    450,
    FALSE,
    6.10,
    6.30,
    6.20,
    6.20,
    'Entry 450W unit,Good for budget GPUs'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = '450W 80+ Bronze PSU');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Office mATX Compact Case',
    'Simple low-cost case for office and study builds',
    'ExeGate',
    1900,
    'RUB',
    TRUE,
    55,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    4.80,
    5.30,
    5.50,
    5.30,
    'Compact budget case,Lowest price case'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Office mATX Compact Case');

INSERT INTO products(name, description, brand, price, currency, in_stock, stock_quantity, category_id, component_type, socket, supported_sockets, ram_type, gpu_tdp, cpu_tdp, psu_watts, supports_wifi, score_gaming, score_work, score_study, score_general, notes)
SELECT
    'Mini Tower Mesh Case',
    'Cheap mesh-front case for budget gaming PCs',
    'Zalman',
    2800,
    'RUB',
    TRUE,
    38,
    (SELECT id FROM categories WHERE slug = 'cases'),
    'CASE',
    NULL,
    NULL,
    NULL,
    0,
    0,
    0,
    FALSE,
    6.10,
    6.00,
    6.10,
    6.00,
    'Affordable airflow case'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Mini Tower Mesh Case');
