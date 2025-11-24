-- Initialize database with sample flight data

-- Insert sample flights for testing
INSERT INTO flights (flight_number, airline_name, departure_datetime, arrival_datetime, origin, destination) VALUES
-- Delhi to Bangalore (Direct)
('AI101', 'Air India', '2025-12-01 06:00:00+00', '2025-12-01 09:00:00+00', 'DEL', 'BLR'),
('6E201', 'IndiGo', '2025-12-01 08:30:00+00', '2025-12-01 11:30:00+00', 'DEL', 'BLR'),
('SG301', 'SpiceJet', '2025-12-01 14:00:00+00', '2025-12-01 17:00:00+00', 'DEL', 'BLR'),

-- Delhi to Hyderabad
('AI201', 'Air India', '2025-12-01 07:00:00+00', '2025-12-01 09:30:00+00', 'DEL', 'HYD'),
('6E301', 'IndiGo', '2025-12-01 12:00:00+00', '2025-12-01 14:30:00+00', 'DEL', 'HYD'),

-- Hyderabad to Bangalore
('AI202', 'Air India', '2025-12-01 11:00:00+00', '2025-12-01 12:15:00+00', 'HYD', 'BLR'),
('6E302', 'IndiGo', '2025-12-01 16:00:00+00', '2025-12-01 17:15:00+00', 'HYD', 'BLR'),

-- Delhi to Mumbai
('AI401', 'Air India', '2025-12-01 06:30:00+00', '2025-12-01 09:00:00+00', 'DEL', 'BOM'),
('6E401', 'IndiGo', '2025-12-01 11:00:00+00', '2025-12-01 13:30:00+00', 'DEL', 'BOM'),

-- Mumbai to Bangalore
('AI402', 'Air India', '2025-12-01 10:00:00+00', '2025-12-01 11:45:00+00', 'BOM', 'BLR'),
('6E402', 'IndiGo', '2025-12-01 15:00:00+00', '2025-12-01 16:45:00+00', 'BOM', 'BLR'),

-- Next day flights for transit routes
('AI203', 'Air India', '2025-12-02 08:00:00+00', '2025-12-02 09:15:00+00', 'HYD', 'BLR'),
('6E303', 'IndiGo', '2025-12-02 10:00:00+00', '2025-12-02 11:15:00+00', 'HYD', 'BLR')
ON CONFLICT DO NOTHING;