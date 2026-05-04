-- Customers
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
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

-- Pension accounts
CREATE TABLE pension_accounts (
    pension_account_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    provider_name VARCHAR(100),
    pension_type VARCHAR(50),
    policy_number VARCHAR(50) UNIQUE,
    current_balance DECIMAL(14,2),
    monthly_contribution DECIMAL(12,2),
    employer_contribution DECIMAL(12,2),
    employee_contribution DECIMAL(12,2),
    start_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Insurance policies
CREATE TABLE insurance_policies (
    insurance_id INT PRIMARY KEY,
    customer_id INT,
    insurance_type VARCHAR(100),
    policy_number VARCHAR(50),
    coverage_amount DECIMAL(14,2),
    monthly_price DECIMAL(12,2),
    active BIT DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Payout information
CREATE TABLE payout_information (
    payout_id INT PRIMARY KEY,
    customer_id INT,
    earliest_payout_age INT,
    expected_retirement_age INT,
    expected_monthly_payout DECIMAL(12,2),
    payout_type VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Tax information
CREATE TABLE tax_information (
    tax_id INT PRIMARY KEY,
    customer_id INT,
    tax_code VARCHAR(50),
    estimated_tax_rate DECIMAL(5,2),
    pal_tax_total DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Cost overview
CREATE TABLE cost_overview (
    cost_id INT PRIMARY KEY,
    pension_account_id INT,
    yearly_cost_percent DECIMAL(5,2),
    yearly_cost_amount DECIMAL(12,2),
    FOREIGN KEY (pension_account_id) REFERENCES pension_accounts(pension_account_id)
);

-- AI overview view
CREATE VIEW customer_ai_overview AS
SELECT 
    c.customer_id,
    c.full_name,
    c.birth_date,
    c.employment_status,
    c.annual_income,
    c.risk_profile,

    p.provider_name,
    p.pension_type,
    p.policy_number,
    p.current_balance,
    p.monthly_contribution,
    p.employer_contribution,
    p.employee_contribution,

    co.yearly_cost_percent,
    co.yearly_cost_amount,

    pi.earliest_payout_age,
    pi.expected_retirement_age,
    pi.expected_monthly_payout,

    t.tax_code,
    t.estimated_tax_rate,
    t.pal_tax_total

FROM customers c
LEFT JOIN pension_accounts p 
    ON c.customer_id = p.customer_id
LEFT JOIN cost_overview co 
    ON p.pension_account_id = co.pension_account_id
LEFT JOIN payout_information pi 
    ON c.customer_id = pi.customer_id
LEFT JOIN tax_information t 
    ON c.customer_id = t.customer_id;