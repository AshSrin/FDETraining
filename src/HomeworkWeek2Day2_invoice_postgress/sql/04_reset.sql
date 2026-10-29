TRUNCATE TABLE invoices;

INSERT INTO invoices (invoice_id, vendor, amount, status, approval) VALUES
('INV001', 'Vendor A', 100.00, 'approved', 'MANAGER_REVIEW'),
('INV002', 'Vendor B', 200.00, 'pending', 'FINANCE_REVIEW'),
('INV003', 'Vendor A', 150.00, 'approved', 'STANDARD_REVIEW'),
('INV004', 'Vendor C', 300.00, 'rejected', 'MANAGER_REVIEW'),
('INV005', 'Vendor B', 250.00, 'approved', 'STANDARD_REVIEW');