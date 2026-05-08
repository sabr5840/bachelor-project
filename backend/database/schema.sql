IF OBJECT_ID('customer_ai_overview', 'V') IS NOT NULL DROP VIEW customer_ai_overview;
IF OBJECT_ID('customer_insurance_overview', 'V') IS NOT NULL DROP VIEW customer_insurance_overview;
IF OBJECT_ID('customer_investment_overview', 'V') IS NOT NULL DROP VIEW customer_investment_overview;
IF OBJECT_ID('customer_return_overview', 'V') IS NOT NULL DROP VIEW customer_return_overview;
IF OBJECT_ID('customer_beneficiary_overview', 'V') IS NOT NULL DROP VIEW customer_beneficiary_overview;
IF OBJECT_ID('customer_contribution_overview', 'V') IS NOT NULL DROP VIEW customer_contribution_overview;
GO

-- Drop tables in dependency order
IF OBJECT_ID('contribution_history', 'U') IS NOT NULL DROP TABLE contribution_history;
IF OBJECT_ID('return_history', 'U') IS NOT NULL DROP TABLE return_history;
IF OBJECT_ID('investment_allocations', 'U') IS NOT NULL DROP TABLE investment_allocations;
IF OBJECT_ID('beneficiaries', 'U') IS NOT NULL DROP TABLE beneficiaries;
IF OBJECT_ID('cost_overview', 'U') IS NOT NULL DROP TABLE cost_overview;
IF OBJECT_ID('tax_information', 'U') IS NOT NULL DROP TABLE tax_information;
IF OBJECT_ID('payout_information', 'U') IS NOT NULL DROP TABLE payout_information;
IF OBJECT_ID('insurance_policies', 'U') IS NOT NULL DROP TABLE insurance_policies;
IF OBJECT_ID('pension_accounts', 'U') IS NOT NULL DROP TABLE pension_accounts;
IF OBJECT_ID('customers', 'U') IS NOT NULL DROP TABLE customers;
GO

CREATE TABLE customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    cpr_number VARCHAR(20) NOT NULL UNIQUE,
    birth_date DATE NOT NULL,
    address VARCHAR(255),
    email VARCHAR(100),
    phone VARCHAR(30),
    employment_status VARCHAR(50),
    annual_income DECIMAL(12,2),
    risk_profile VARCHAR(30),
    created_at DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE pension_accounts (
    pension_account_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    provider_name VARCHAR(100),
    pension_type VARCHAR(50) NOT NULL,
    policy_number VARCHAR(50) UNIQUE,
    current_balance DECIMAL(14,2),
    monthly_contribution DECIMAL(12,2),
    monthly_company_contribution DECIMAL(12,2),
    monthly_customer_contribution DECIMAL(12,2),
    start_date DATE,
    active BIT DEFAULT 1,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

CREATE TABLE insurance_policies (
    insurance_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    insurance_type VARCHAR(100) NOT NULL,
    policy_number VARCHAR(50),
    coverage_amount DECIMAL(14,2),
    monthly_price DECIMAL(12,2),
    coverage_description VARCHAR(500),
    claim_process VARCHAR(1000),
    waiting_period VARCHAR(100),
    expires_at DATE,
    active BIT DEFAULT 1,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

CREATE TABLE payout_information (
    payout_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    earliest_payout_age INT,
    expected_retirement_age INT,
    expected_monthly_payout DECIMAL(12,2),
    payout_type VARCHAR(50),
    payout_start_date DATE,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

CREATE TABLE tax_information (
    tax_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    tax_code VARCHAR(50),
    estimated_tax_rate DECIMAL(5,2),
    pal_tax_total DECIMAL(12,2),
    last_updated DATE DEFAULT GETDATE(),

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

CREATE TABLE cost_overview (
    cost_id INT IDENTITY(1,1) PRIMARY KEY,
    pension_account_id INT NOT NULL,
    yearly_cost_percent DECIMAL(5,2),
    yearly_cost_amount DECIMAL(12,2),
    administration_fee_monthly DECIMAL(12,2),
    investment_cost_amount DECIMAL(12,2),

    FOREIGN KEY (pension_account_id) REFERENCES pension_accounts(pension_account_id)
);
GO

CREATE TABLE investment_allocations (
    allocation_id INT IDENTITY(1,1) PRIMARY KEY,
    pension_account_id INT NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    allocation_percent DECIMAL(5,2) NOT NULL,
    risk_level VARCHAR(50),

    FOREIGN KEY (pension_account_id) REFERENCES pension_accounts(pension_account_id)
);
GO

CREATE TABLE return_history (
    return_id INT IDENTITY(1,1) PRIMARY KEY,
    pension_account_id INT NOT NULL,
    return_year INT NOT NULL,
    return_percent DECIMAL(5,2),
    return_amount DECIMAL(12,2),

    FOREIGN KEY (pension_account_id) REFERENCES pension_accounts(pension_account_id)
);
GO

CREATE TABLE contribution_history (
    contribution_id INT IDENTITY(1,1) PRIMARY KEY,
    pension_account_id INT NOT NULL,
    contribution_date DATE NOT NULL,
    company_amount DECIMAL(12,2),
    customer_amount DECIMAL(12,2),
    total_amount DECIMAL(12,2),

    FOREIGN KEY (pension_account_id) REFERENCES pension_accounts(pension_account_id)
);
GO

CREATE TABLE beneficiaries (
    beneficiary_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    relation VARCHAR(50),
    percentage DECIMAL(5,2),
    is_primary BIT DEFAULT 1,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

CREATE VIEW customer_ai_overview AS
SELECT
    c.customer_id,
    c.full_name,
    c.birth_date,
    c.employment_status,
    c.annual_income,
    c.risk_profile,

    p.pension_account_id,
    p.provider_name,
    p.pension_type,
    p.policy_number,
    p.current_balance,
    p.monthly_contribution,
    p.monthly_company_contribution,
    p.monthly_customer_contribution,
    p.start_date,
    p.active AS pension_active,

    co.yearly_cost_percent,
    co.yearly_cost_amount,
    co.administration_fee_monthly,
    co.investment_cost_amount,

    pi.earliest_payout_age,
    pi.expected_retirement_age,
    pi.expected_monthly_payout,
    pi.payout_type,
    pi.payout_start_date,

    t.tax_code,
    t.estimated_tax_rate,
    t.pal_tax_total,
    t.last_updated AS tax_last_updated

FROM customers c
LEFT JOIN pension_accounts p
    ON c.customer_id = p.customer_id
LEFT JOIN cost_overview co
    ON p.pension_account_id = co.pension_account_id
LEFT JOIN payout_information pi
    ON c.customer_id = pi.customer_id
LEFT JOIN tax_information t
    ON c.customer_id = t.customer_id;
GO

CREATE VIEW customer_insurance_overview AS
SELECT
    c.customer_id,
    c.full_name,
    i.insurance_type,
    i.policy_number,
    i.coverage_amount,
    i.monthly_price,
    i.coverage_description,
    i.claim_process,
    i.waiting_period,
    i.expires_at,
    i.active
FROM customers c
LEFT JOIN insurance_policies i
    ON c.customer_id = i.customer_id;
GO

CREATE VIEW customer_investment_overview AS
SELECT
    c.customer_id,
    c.full_name,
    p.pension_account_id,
    p.pension_type,
    p.policy_number,
    ia.asset_type,
    ia.allocation_percent,
    ia.risk_level
FROM customers c
LEFT JOIN pension_accounts p
    ON c.customer_id = p.customer_id
LEFT JOIN investment_allocations ia
    ON p.pension_account_id = ia.pension_account_id;
GO

CREATE VIEW customer_return_overview AS
SELECT
    c.customer_id,
    c.full_name,
    p.pension_account_id,
    p.pension_type,
    p.policy_number,
    rh.return_year,
    rh.return_percent,
    rh.return_amount
FROM customers c
LEFT JOIN pension_accounts p
    ON c.customer_id = p.customer_id
LEFT JOIN return_history rh
    ON p.pension_account_id = rh.pension_account_id;
GO

CREATE VIEW customer_beneficiary_overview AS
SELECT
    c.customer_id,
    c.full_name,
    b.full_name AS beneficiary_name,
    b.relation,
    b.percentage,
    b.is_primary
FROM customers c
LEFT JOIN beneficiaries b
    ON c.customer_id = b.customer_id;
GO

CREATE VIEW customer_contribution_overview AS
SELECT
    c.customer_id,
    c.full_name,
    p.pension_account_id,
    p.pension_type,
    p.policy_number,
    ch.contribution_date,
    ch.company_amount,
    ch.customer_amount,
    ch.total_amount
FROM customers c
LEFT JOIN pension_accounts p
    ON c.customer_id = p.customer_id
LEFT JOIN contribution_history ch
    ON p.pension_account_id = ch.pension_account_id;
GO