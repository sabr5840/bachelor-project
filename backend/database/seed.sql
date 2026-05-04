-- Customer
INSERT INTO customers VALUES (
    1,
    'Mette Larsen',
    '120389-1234',
    '1989-03-12',
    'Aarhus',
    'mette@test.dk',
    '12345678',
    'Fuldtidsansat',
    504000,
    'Middel',
    GETDATE()
);

-- Pension accounts
INSERT INTO pension_accounts VALUES
(
    1, 1, 'PenSam', 'Ratepension',
    'POL-10001', 485000, 4200, 2800, 1400, '2016-01-01'
),
(
    2, 1, 'PenSam', 'Livrente',
    'POL-10002', 210000, 1600, 1000, 600, '2018-04-01'
);

-- Insurance
INSERT INTO insurance_policies VALUES
(
    1, 1, 'Kritisk sygdom',
    'INS-1', 150000, 95, 1
);

-- Payout
INSERT INTO payout_information VALUES
(
    1, 1, 60, 67, 18500, 'Månedlig'
);

-- Tax
INSERT INTO tax_information VALUES
(
    1, 1, 'A-skat', 37.00, 7300
);

-- Costs
INSERT INTO cost_overview VALUES
(
    1, 1, 1.10, 5335
),
(
    2, 2, 1.25, 2625
);
