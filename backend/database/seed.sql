
-- ============================================================
-- CUSTOMERS
-- ============================================================

INSERT INTO customers (
    full_name,
    cpr_number,
    birth_date,
    address,
    email,
    phone,
    employment_status,
    annual_income,
    risk_profile
)
VALUES
('Mette Larsen', '120389-1234', '1989-03-12', 'Aarhus', 'mette@test.dk', '12345678', 'Fuldtidsansat', 504000, 'Middel'),
('Anne Jensen', '230591-2234', '1991-05-23', 'Odense', 'anne@test.dk', '22334455', 'Fuldtidsansat', 420000, 'Middel'),
('Lars Nielsen', '150782-5432', '1982-07-15', 'København', 'lars@test.dk', '33445566', 'Fuldtidsansat', 620000, 'Høj'),
('Sofie Hansen', '110299-8888', '1999-02-11', 'Aalborg', 'sofie@test.dk', '99887766', 'Deltidsansat', 280000, 'Lav'),
('Camilla Pedersen', '010184-2222', '1984-01-01', 'Esbjerg', 'camilla@test.dk', '66554433', 'Fuldtidsansat', 540000, 'Middel'),
('Jonas Madsen', '170676-9999', '1976-06-17', 'Randers', 'jonas@test.dk', '11223344', 'Fuldtidsansat', 700000, 'Høj'),
('Maria Kristensen', '030393-7777', '1993-03-03', 'Horsens', 'maria@test.dk', '44556677', 'Fuldtidsansat', 460000, 'Middel'),
('Peter Andersen', '090970-1111', '1970-09-09', 'Kolding', 'peter@test.dk', '55667788', 'Fuldtidsansat', 780000, 'Lav'),
('Louise Holm', '120695-4545', '1995-06-12', 'Silkeborg', 'louise@test.dk', '66778899', 'Fuldtidsansat', 390000, 'Middel'),
('Rasmus Thomsen', '220881-7878', '1981-08-22', 'Roskilde', 'rasmus@test.dk', '77889900', 'Fuldtidsansat', 650000, 'Høj'),
('Line Sørensen', '040287-1919', '1987-02-04', 'Herning', 'line@test.dk', '19191919', 'Fuldtidsansat', 510000, 'Middel'),
('Henrik Poulsen', '020468-1212', '1968-04-02', 'Vejle', 'henrik@test.dk', '12121212', 'Fuldtidsansat', 820000, 'Lav'),
('Julie Dahl', '070998-6767', '1998-09-07', 'Næstved', 'julie@test.dk', '67676767', 'Deltidsansat', 250000, 'Lav'),
('Thomas Lund', '150785-8989', '1985-07-15', 'Køge', 'thomas@test.dk', '89898989', 'Fuldtidsansat', 590000, 'Middel'),
('Emma Frederiksen', '011190-9090', '1990-11-01', 'Fredericia', 'emma@test.dk', '90909090', 'Fuldtidsansat', 470000, 'Middel');


-- ============================================================
-- PENSION ACCOUNTS
-- Typisk pensionsbidrag: ca. 12% af løn
-- 8% arbejdsgiver / 4% medarbejder
-- ============================================================

INSERT INTO pension_accounts (
    customer_id,
    provider_name,
    pension_type,
    policy_number,
    current_balance,
    monthly_contribution,
    employer_contribution,
    employee_contribution,
    start_date,
    active
)
VALUES
(1, 'PenSam', 'Ratepension', 'POL-10001', 485000, 4200, 2800, 1400, '2016-01-01', 1),
(1, 'PenSam', 'Livrente', 'POL-10002', 210000, 1600, 1000, 600, '2018-04-01', 1),

(2, 'PenSam', 'Ratepension', 'POL-10003', 290000, 3500, 2333, 1167, '2017-01-01', 1),
(2, 'PenSam', 'Aldersopsparing', 'POL-10004', 65000, 700, 0, 700, '2021-01-01', 1),

(3, 'PenSam', 'Livrente', 'POL-10005', 880000, 6200, 4133, 2067, '2010-01-01', 1),
(3, 'PenSam', 'Ratepension', 'POL-10006', 430000, 0, 0, 0, '2012-03-01', 1),

(4, 'PenSam', 'Aldersopsparing', 'POL-10007', 45000, 1800, 1200, 600, '2022-01-01', 1),

(5, 'PenSam', 'Ratepension', 'POL-10008', 520000, 4500, 3000, 1500, '2014-01-01', 1),
(5, 'PenSam', 'Livrente', 'POL-10009', 260000, 900, 600, 300, '2016-06-01', 1),

(6, 'PenSam', 'Livrente', 'POL-10010', 1400000, 7000, 4667, 2333, '2001-01-01', 1),
(6, 'PenSam', 'Ratepension', 'POL-10011', 620000, 0, 0, 0, '2006-01-01', 1),

(7, 'PenSam', 'Ratepension', 'POL-10012', 310000, 3800, 2533, 1267, '2019-01-01', 1),

(8, 'PenSam', 'Livrente', 'POL-10013', 1800000, 7800, 5200, 2600, '1998-01-01', 1),
(8, 'PenSam', 'Ratepension', 'POL-10014', 850000, 0, 0, 0, '2003-01-01', 1),

(9, 'PenSam', 'Ratepension', 'POL-10015', 140000, 3200, 2133, 1067, '2020-01-01', 1),
(9, 'PenSam', 'Aldersopsparing', 'POL-10016', 35000, 500, 0, 500, '2022-01-01', 1),

(10, 'PenSam', 'Livrente', 'POL-10017', 970000, 6500, 4333, 2167, '2008-01-01', 1),
(10, 'PenSam', 'Ratepension', 'POL-10018', 510000, 0, 0, 0, '2011-01-01', 1),

(11, 'PenSam', 'Ratepension', 'POL-10019', 560000, 4250, 2833, 1417, '2015-01-01', 1),
(11, 'PenSam', 'Livrente', 'POL-10020', 240000, 850, 567, 283, '2017-01-01', 1),

(12, 'PenSam', 'Livrente', 'POL-10021', 2100000, 8200, 5467, 2733, '1996-01-01', 1),
(12, 'PenSam', 'Ratepension', 'POL-10022', 900000, 0, 0, 0, '2001-01-01', 1),

(13, 'PenSam', 'Aldersopsparing', 'POL-10023', 28000, 1700, 1133, 567, '2023-01-01', 1),

(14, 'PenSam', 'Ratepension', 'POL-10024', 610000, 4900, 3267, 1633, '2013-01-01', 1),
(14, 'PenSam', 'Livrente', 'POL-10025', 300000, 1000, 667, 333, '2015-01-01', 1),

(15, 'PenSam', 'Ratepension', 'POL-10026', 360000, 3900, 2600, 1300, '2018-01-01', 1),
(15, 'PenSam', 'Aldersopsparing', 'POL-10027', 75000, 700, 0, 700, '2021-01-01', 1);


-- ============================================================
-- INSURANCE POLICIES
-- PenSam-lignende forsikringssetup baseret på rådgiverinput
-- ============================================================

INSERT INTO insurance_policies (
    customer_id,
    insurance_type,
    policy_number,
    coverage_amount,
    monthly_price,
    coverage_description,
    claim_process,
    waiting_period,
    expires_at,
    active
)
VALUES
-- Kunde 1
(1, 'Sundhedsordning', 'INS-1001', 0, 85, 'Dækker fysioterapi, kiropraktor, psykolog og diætist med typisk 6-12 behandlinger om året.', 'Book behandling via sundhedsordningens selvbetjening eller kontakt pensionsselskabet.', 'Ingen', NULL, 1),
(1, 'Kritisk sygdom', 'INS-1002', 100000, 95, 'Gruppesum ved visse kritiske sygdomme, fx kræft, hjernesvulst eller Alzheimers.', 'Anmeld sygdommen og indsend lægelig dokumentation.', 'Ingen', NULL, 1),
(1, 'Gruppeliv', 'INS-1003', 475000, 120, 'Skattefri dødsfaldsdækning til begunstigede eller nærmeste pårørende.', 'Udbetales ved dødsfald efter sagsbehandling.', 'Ingen', NULL, 1),
(1, 'Børnepension', 'INS-1004', 5000, 35, 'Årlig udbetaling før skat til børn under 21 år ved dødsfald.', 'Udbetales til berettigede børn ved dødsfald.', 'Ingen', NULL, 1),
(1, 'Præmiefritagelse', 'INS-1005', 0, 40, 'PenSam overtager pensionsindbetalinger ved tilkendt offentlig førtidspension.', 'Kræver dokumentation for offentlig førtidspension.', 'Ingen', NULL, 1),

-- Kunde 2
(2, 'Sundhedsordning', 'INS-1006', 0, 80, 'Dækker fysioterapi, kiropraktor, psykolog og diætist med typisk 6-12 behandlinger om året.', 'Book behandling via sundhedsordningens selvbetjening.', 'Ingen', NULL, 1),
(2, 'Kritisk sygdom', 'INS-1007', 100000, 90, 'Skattefri gruppesum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(2, 'Gruppeliv', 'INS-1008', 475000, 115, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),
(2, 'Præmiefritagelse', 'INS-1009', 0, 35, 'Pensionsindbetalinger overtages ved offentlig førtidspension.', 'Kræver offentlig tilkendelse.', 'Ingen', NULL, 1),

-- Kunde 3
(3, 'Sundhedsordning', 'INS-1010', 0, 90, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(3, 'Førtidspension', 'INS-1011', 20000, 145, 'Løbende årlig udbetaling før skat ved offentlig førtidspension eller seniorpension.', 'Kræver offentlig tilkendelse.', 'Ingen', NULL, 1),
(3, 'Gruppesum ved førtidspension', 'INS-1012', 100000, 70, 'Skattefri engangsudbetaling ved offentlig førtidspension.', 'Kræver dokumentation for offentlig førtidspension.', 'Ingen', NULL, 1),
(3, 'Gruppeliv', 'INS-1013', 475000, 120, 'Skattefri dødsfaldsdækning.', 'Udbetales til begunstigede.', 'Ingen', NULL, 1),

-- Kunde 4
(4, 'Sundhedsordning', 'INS-1014', 0, 65, 'Dækker behandlinger som fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsordning.', 'Ingen', NULL, 1),
(4, 'Kritisk sygdom', 'INS-1015', 100000, 70, 'Skattefri sum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(4, 'Gruppeliv', 'INS-1016', 475000, 95, 'Dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),

-- Kunde 5
(5, 'Sundhedsordning', 'INS-1017', 0, 85, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsordning.', 'Ingen', NULL, 1),
(5, 'Kritisk sygdom', 'INS-1018', 100000, 95, 'Skattefri sum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(5, 'Gruppeliv', 'INS-1019', 475000, 120, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),
(5, 'Børnepension', 'INS-1020', 5000, 35, 'Årlig udbetaling før skat til børn under 21 år ved dødsfald.', 'Udbetales til berettigede børn.', 'Ingen', NULL, 1),

-- Kunde 6
(6, 'Sundhedsordning', 'INS-1021', 0, 90, 'Dækker behandlinger inden for fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(6, 'Førtidspension', 'INS-1022', 20000, 150, 'Løbende årlig udbetaling før skat ved offentlig førtidspension eller seniorpension.', 'Kræver offentlig tilkendelse.', 'Ingen', NULL, 1),
(6, 'Gruppesum ved førtidspension', 'INS-1023', 100000, 75, 'Skattefri engangsudbetaling ved offentlig førtidspension.', 'Kræver dokumentation.', 'Ingen', NULL, 1),
(6, 'Gruppeliv', 'INS-1024', 475000, 130, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),

-- Kunde 7
(7, 'Sundhedsordning', 'INS-1025', 0, 82, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(7, 'Kritisk sygdom', 'INS-1026', 100000, 92, 'Skattefri gruppesum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(7, 'Gruppeliv', 'INS-1027', 475000, 115, 'Skattefri dødsfaldsdækning.', 'Udbetales til begunstigede.', 'Ingen', NULL, 1),
(7, 'Præmiefritagelse', 'INS-1028', 0, 35, 'PenSam overtager pensionsindbetalinger ved tilkendt offentlig førtidspension.', 'Kræver dokumentation.', 'Ingen', NULL, 1),

-- Kunde 8
(8, 'Sundhedsordning', 'INS-1029', 0, 90, 'Dækker behandlinger inden for fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsordning.', 'Ingen', NULL, 1),
(8, 'Gruppeliv', 'INS-1030', 475000, 130, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),
(8, 'Præmiefritagelse', 'INS-1031', 0, 40, 'Pensionsindbetalinger overtages ved offentlig førtidspension.', 'Kræver offentlig tilkendelse.', 'Ingen', NULL, 1),

-- Kunde 9
(9, 'Sundhedsordning', 'INS-1032', 0, 75, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(9, 'Kritisk sygdom', 'INS-1033', 100000, 85, 'Skattefri sum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(9, 'Gruppeliv', 'INS-1034', 475000, 105, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),

-- Kunde 10
(10, 'Sundhedsordning', 'INS-1035', 0, 90, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsordning.', 'Ingen', NULL, 1),
(10, 'Førtidspension', 'INS-1036', 20000, 150, 'Løbende årlig udbetaling før skat ved offentlig førtidspension eller seniorpension.', 'Kræver offentlig tilkendelse.', 'Ingen', NULL, 1),
(10, 'Gruppeliv', 'INS-1037', 475000, 125, 'Skattefri dødsfaldsdækning.', 'Udbetales til begunstigede.', 'Ingen', NULL, 1),
(10, 'Børnepension', 'INS-1038', 5000, 35, 'Årlig udbetaling før skat til børn under 21 år ved dødsfald.', 'Udbetales til berettigede børn.', 'Ingen', NULL, 1),

-- Kunde 11
(11, 'Sundhedsordning', 'INS-1039', 0, 85, 'Dækker behandlinger som fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(11, 'Kritisk sygdom', 'INS-1040', 100000, 95, 'Skattefri gruppesum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(11, 'Gruppeliv', 'INS-1041', 475000, 120, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),

-- Kunde 12
(12, 'Sundhedsordning', 'INS-1042', 0, 90, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsordning.', 'Ingen', NULL, 1),
(12, 'Gruppeliv', 'INS-1043', 475000, 130, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),
(12, 'Præmiefritagelse', 'INS-1044', 0, 45, 'PenSam overtager pensionsindbetalinger ved offentlig førtidspension.', 'Kræver offentlig tilkendelse.', 'Ingen', NULL, 1),

-- Kunde 13
(13, 'Sundhedsordning', 'INS-1045', 0, 65, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(13, 'Kritisk sygdom', 'INS-1046', 100000, 70, 'Skattefri sum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(13, 'Gruppeliv', 'INS-1047', 475000, 95, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1),

-- Kunde 14
(14, 'Sundhedsordning', 'INS-1048', 0, 88, 'Dækker fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsordning.', 'Ingen', NULL, 1),
(14, 'Kritisk sygdom', 'INS-1049', 100000, 95, 'Skattefri gruppesum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(14, 'Gruppeliv', 'INS-1050', 475000, 120, 'Skattefri dødsfaldsdækning.', 'Udbetales til begunstigede.', 'Ingen', NULL, 1),
(14, 'Børnepension', 'INS-1051', 5000, 35, 'Årlig udbetaling før skat til børn under 21 år ved dødsfald.', 'Udbetales til berettigede børn.', 'Ingen', NULL, 1),

-- Kunde 15
(15, 'Sundhedsordning', 'INS-1052', 0, 83, 'Dækker behandlinger som fysioterapi, kiropraktor, psykolog og diætist.', 'Booking via sundhedsportal.', 'Ingen', NULL, 1),
(15, 'Kritisk sygdom', 'INS-1053', 100000, 90, 'Skattefri sum ved visse kritiske sygdomme.', 'Anmeldelse med lægelig dokumentation.', 'Ingen', NULL, 1),
(15, 'Gruppeliv', 'INS-1054', 475000, 115, 'Skattefri dødsfaldsdækning.', 'Udbetales ved dødsfald.', 'Ingen', NULL, 1);


-- ============================================================
-- PAYOUT INFORMATION
-- ============================================================

INSERT INTO payout_information (
    customer_id,
    earliest_payout_age,
    expected_retirement_age,
    expected_monthly_payout,
    payout_type,
    payout_start_date
)
VALUES
(1, 60, 67, 18500, 'Månedlig', '2056-03-01'),
(2, 62, 68, 14200, 'Månedlig', '2059-05-01'),
(3, 60, 67, 28000, 'Livsvarig', '2049-07-01'),
(4, 65, 69, 9500, 'Månedlig', '2068-02-01'),
(5, 60, 67, 20500, 'Månedlig', '2051-01-01'),
(6, 60, 67, 33500, 'Livsvarig', '2043-06-01'),
(7, 62, 68, 16000, 'Månedlig', '2061-03-01'),
(8, 60, 67, 36500, 'Livsvarig', '2037-09-01'),
(9, 62, 68, 12500, 'Månedlig', '2063-06-01'),
(10, 60, 67, 29500, 'Livsvarig', '2048-08-01'),
(11, 60, 67, 19500, 'Månedlig', '2054-02-01'),
(12, 60, 67, 39000, 'Livsvarig', '2035-04-01'),
(13, 65, 69, 8200, 'Månedlig', '2067-09-01'),
(14, 60, 67, 22500, 'Månedlig', '2052-07-01'),
(15, 62, 68, 17200, 'Månedlig', '2058-11-01');


-- ============================================================
-- TAX INFORMATION
-- ============================================================

INSERT INTO tax_information (
    customer_id,
    tax_code,
    estimated_tax_rate,
    pal_tax_total,
    last_updated
)
VALUES
(1, 'A-skat', 37.00, 7300, GETDATE()),
(2, 'A-skat', 36.00, 4200, GETDATE()),
(3, 'A-skat', 41.00, 16200, GETDATE()),
(4, 'A-skat', 34.00, 1100, GETDATE()),
(5, 'A-skat', 38.00, 8200, GETDATE()),
(6, 'A-skat', 42.00, 24500, GETDATE()),
(7, 'A-skat', 36.50, 5100, GETDATE()),
(8, 'A-skat', 42.00, 31000, GETDATE()),
(9, 'A-skat', 35.00, 2600, GETDATE()),
(10, 'A-skat', 41.00, 18500, GETDATE()),
(11, 'A-skat', 37.50, 7900, GETDATE()),
(12, 'A-skat', 43.00, 36000, GETDATE()),
(13, 'A-skat', 33.00, 900, GETDATE()),
(14, 'A-skat', 39.00, 9300, GETDATE()),
(15, 'A-skat', 36.50, 5400, GETDATE());


-- ============================================================
-- COST OVERVIEW
-- One row per pension account
-- ============================================================

INSERT INTO cost_overview (
    pension_account_id,
    yearly_cost_percent,
    yearly_cost_amount,
    administration_fee_monthly,
    investment_cost_amount
)
VALUES
(1, 1.10, 5335, 45, 3200),
(2, 1.25, 2625, 35, 1700),
(3, 1.08, 3132, 40, 2100),
(4, 0.95, 618, 25, 380),
(5, 1.05, 9240, 55, 6500),
(6, 1.12, 4816, 45, 3100),
(7, 0.95, 428, 25, 180),
(8, 1.10, 5720, 45, 3500),
(9, 1.20, 3120, 35, 1900),
(10, 1.00, 14000, 60, 9200),
(11, 1.08, 6696, 50, 4200),
(12, 1.12, 3348, 40, 2200),
(13, 1.15, 20700, 65, 14200),
(14, 1.10, 9350, 55, 6000),
(15, 1.05, 1470, 30, 900),
(16, 0.92, 322, 25, 150),
(17, 1.04, 10088, 55, 6600),
(18, 1.12, 5712, 45, 3500),
(19, 1.10, 6160, 45, 3900),
(20, 1.20, 2880, 35, 1700),
(21, 0.98, 20580, 65, 13500),
(22, 1.08, 9720, 55, 6200),
(23, 0.90, 252, 25, 120),
(24, 1.05, 6405, 45, 4000),
(25, 1.18, 3540, 35, 2300),
(26, 1.08, 3888, 40, 2400),
(27, 0.92, 690, 25, 320);


-- ============================================================
-- INVESTMENT ALLOCATIONS
-- 3 rows per pension account
-- Allocation always totals 100%
-- ============================================================

INSERT INTO investment_allocations (
    pension_account_id,
    asset_type,
    allocation_percent,
    risk_level
)
VALUES
-- Account 1 Middel
(1, 'Aktier', 55, 'Middel'), (1, 'Obligationer', 35, 'Middel'), (1, 'Ejendomme', 10, 'Middel'),
-- Account 2 Lav
(2, 'Aktier', 45, 'Lav'), (2, 'Obligationer', 45, 'Lav'), (2, 'Ejendomme', 10, 'Lav'),
-- Account 3 Middel
(3, 'Aktier', 55, 'Middel'), (3, 'Obligationer', 35, 'Middel'), (3, 'Ejendomme', 10, 'Middel'),
-- Account 4 Lav
(4, 'Aktier', 35, 'Lav'), (4, 'Obligationer', 55, 'Lav'), (4, 'Ejendomme', 10, 'Lav'),
-- Account 5 Høj
(5, 'Aktier', 75, 'Høj'), (5, 'Obligationer', 15, 'Høj'), (5, 'Alternative investeringer', 10, 'Høj'),
-- Account 6 Høj
(6, 'Aktier', 75, 'Høj'), (6, 'Obligationer', 15, 'Høj'), (6, 'Alternative investeringer', 10, 'Høj'),
-- Account 7 Lav
(7, 'Aktier', 30, 'Lav'), (7, 'Obligationer', 60, 'Lav'), (7, 'Ejendomme', 10, 'Lav'),
-- Account 8 Middel
(8, 'Aktier', 55, 'Middel'), (8, 'Obligationer', 35, 'Middel'), (8, 'Ejendomme', 10, 'Middel'),
-- Account 9 Middel
(9, 'Aktier', 55, 'Middel'), (9, 'Obligationer', 35, 'Middel'), (9, 'Ejendomme', 10, 'Middel'),
-- Account 10 Høj
(10, 'Aktier', 80, 'Høj'), (10, 'Obligationer', 10, 'Høj'), (10, 'Alternative investeringer', 10, 'Høj'),
-- Account 11 Høj
(11, 'Aktier', 80, 'Høj'), (11, 'Obligationer', 10, 'Høj'), (11, 'Alternative investeringer', 10, 'Høj'),
-- Account 12 Middel
(12, 'Aktier', 55, 'Middel'), (12, 'Obligationer', 35, 'Middel'), (12, 'Ejendomme', 10, 'Middel'),
-- Account 13 Lav
(13, 'Aktier', 35, 'Lav'), (13, 'Obligationer', 55, 'Lav'), (13, 'Ejendomme', 10, 'Lav'),
-- Account 14 Lav
(14, 'Aktier', 30, 'Lav'), (14, 'Obligationer', 60, 'Lav'), (14, 'Ejendomme', 10, 'Lav'),
-- Account 15 Middel
(15, 'Aktier', 55, 'Middel'), (15, 'Obligationer', 35, 'Middel'), (15, 'Ejendomme', 10, 'Middel'),
-- Account 16 Middel
(16, 'Aktier', 50, 'Middel'), (16, 'Obligationer', 40, 'Middel'), (16, 'Ejendomme', 10, 'Middel'),
-- Account 17 Høj
(17, 'Aktier', 75, 'Høj'), (17, 'Obligationer', 15, 'Høj'), (17, 'Alternative investeringer', 10, 'Høj'),
-- Account 18 Høj
(18, 'Aktier', 75, 'Høj'), (18, 'Obligationer', 15, 'Høj'), (18, 'Alternative investeringer', 10, 'Høj'),
-- Account 19 Middel
(19, 'Aktier', 55, 'Middel'), (19, 'Obligationer', 35, 'Middel'), (19, 'Ejendomme', 10, 'Middel'),
-- Account 20 Middel
(20, 'Aktier', 50, 'Middel'), (20, 'Obligationer', 40, 'Middel'), (20, 'Ejendomme', 10, 'Middel'),
-- Account 21 Lav
(21, 'Aktier', 30, 'Lav'), (21, 'Obligationer', 60, 'Lav'), (21, 'Ejendomme', 10, 'Lav'),
-- Account 22 Lav
(22, 'Aktier', 30, 'Lav'), (22, 'Obligationer', 60, 'Lav'), (22, 'Ejendomme', 10, 'Lav'),
-- Account 23 Lav
(23, 'Aktier', 35, 'Lav'), (23, 'Obligationer', 55, 'Lav'), (23, 'Ejendomme', 10, 'Lav'),
-- Account 24 Middel
(24, 'Aktier', 55, 'Middel'), (24, 'Obligationer', 35, 'Middel'), (24, 'Ejendomme', 10, 'Middel'),
-- Account 25 Middel
(25, 'Aktier', 50, 'Middel'), (25, 'Obligationer', 40, 'Middel'), (25, 'Ejendomme', 10, 'Middel'),
-- Account 26 Middel
(26, 'Aktier', 55, 'Middel'), (26, 'Obligationer', 35, 'Middel'), (26, 'Ejendomme', 10, 'Middel'),
-- Account 27 Middel
(27, 'Aktier', 50, 'Middel'), (27, 'Obligationer', 40, 'Middel'), (27, 'Ejendomme', 10, 'Middel');


-- ============================================================
-- RETURN HISTORY
-- 2021-2024 per pension account
-- ============================================================

INSERT INTO return_history (
    pension_account_id,
    return_year,
    return_percent,
    return_amount
)
VALUES
(1, 2021, 5.20, 21000), (1, 2022, -8.10, -34000), (1, 2023, 7.80, 36000), (1, 2024, 6.10, 31000),
(2, 2021, 4.80, 12000), (2, 2022, -6.40, -14000), (2, 2023, 6.90, 17000), (2, 2024, 5.50, 15000),
(3, 2021, 5.00, 13500), (3, 2022, -7.50, -20500), (3, 2023, 7.40, 21500), (3, 2024, 5.90, 17100),
(4, 2021, 3.10, 1600), (4, 2022, -4.20, -2300), (4, 2023, 4.90, 3100), (4, 2024, 4.10, 2600),
(5, 2021, 7.20, 59000), (5, 2022, -10.80, -95000), (5, 2023, 9.60, 83000), (5, 2024, 7.40, 65100),
(6, 2021, 7.00, 31000), (6, 2022, -10.50, -46500), (6, 2023, 9.40, 40500), (6, 2024, 7.20, 31000),
(7, 2021, 3.80, 1600), (7, 2022, -4.90, -2200), (7, 2023, 5.10, 2300), (7, 2024, 4.30, 1950),
(8, 2021, 5.30, 25000), (8, 2022, -8.00, -39000), (8, 2023, 7.60, 36500), (8, 2024, 6.00, 31200),
(9, 2021, 5.00, 12000), (9, 2022, -7.60, -19000), (9, 2023, 7.30, 18500), (9, 2024, 5.80, 15100),
(10, 2021, 7.60, 98000), (10, 2022, -11.30, -158000), (10, 2023, 10.10, 130000), (10, 2024, 7.90, 110600),
(11, 2021, 7.40, 42000), (11, 2022, -10.90, -67500), (11, 2023, 9.80, 60600), (11, 2024, 7.60, 47100),
(12, 2021, 5.10, 15000), (12, 2022, -7.40, -19500), (12, 2023, 7.20, 17500), (12, 2024, 5.80, 13900),
(13, 2021, 3.60, 61000), (13, 2022, -5.20, -93600), (13, 2023, 5.80, 104400), (13, 2024, 4.70, 84600),
(14, 2021, 3.40, 25500), (14, 2022, -5.00, -42500), (14, 2023, 5.50, 46750), (14, 2024, 4.60, 39100),
(15, 2021, 5.10, 6400), (15, 2022, -7.20, -10100), (15, 2023, 7.10, 9900), (15, 2024, 5.70, 7980),
(16, 2021, 4.90, 1500), (16, 2022, -6.80, -2300), (16, 2023, 6.80, 2350), (16, 2024, 5.30, 1850),
(17, 2021, 7.30, 67000), (17, 2022, -11.00, -106700), (17, 2023, 9.90, 96000), (17, 2024, 7.70, 74700),
(18, 2021, 7.10, 35000), (18, 2022, -10.70, -54500), (18, 2023, 9.50, 48500), (18, 2024, 7.50, 38250),
(19, 2021, 5.20, 26500), (19, 2022, -7.90, -44200), (19, 2023, 7.70, 43100), (19, 2024, 6.00, 33600),
(20, 2021, 4.90, 11500), (20, 2022, -7.00, -16800), (20, 2023, 7.00, 16800), (20, 2024, 5.40, 12960),
(21, 2021, 3.50, 69000), (21, 2022, -5.30, -111300), (21, 2023, 5.90, 123900), (21, 2024, 4.80, 100800),
(22, 2021, 3.40, 29000), (22, 2022, -5.10, -45900), (22, 2023, 5.70, 51300), (22, 2024, 4.60, 41400),
(23, 2021, 3.20, 850), (23, 2022, -4.30, -1200), (23, 2023, 4.80, 1340), (23, 2024, 4.00, 1120),
(24, 2021, 5.20, 29000), (24, 2022, -7.80, -47500), (24, 2023, 7.60, 46300), (24, 2024, 6.00, 36600),
(25, 2021, 4.80, 13000), (25, 2022, -7.10, -21300), (25, 2023, 7.00, 21000), (25, 2024, 5.50, 16500),
(26, 2021, 5.00, 17000), (26, 2022, -7.60, -27400), (26, 2023, 7.40, 26600), (26, 2024, 5.90, 21200),
(27, 2021, 4.70, 3300), (27, 2022, -6.90, -5200), (27, 2023, 6.70, 5000), (27, 2024, 5.30, 3980);


-- ============================================================
-- CONTRIBUTION HISTORY
-- Three recent months per active account
-- ============================================================

INSERT INTO contribution_history (
    pension_account_id,
    contribution_date,
    employer_amount,
    employee_amount,
    total_amount
)
VALUES
(1, '2024-01-01', 2800, 1400, 4200), (1, '2024-02-01', 2800, 1400, 4200), (1, '2024-03-01', 2800, 1400, 4200),
(2, '2024-01-01', 1000, 600, 1600), (2, '2024-02-01', 1000, 600, 1600), (2, '2024-03-01', 1000, 600, 1600),
(3, '2024-01-01', 2333, 1167, 3500), (3, '2024-02-01', 2333, 1167, 3500), (3, '2024-03-01', 2333, 1167, 3500),
(4, '2024-01-01', 0, 700, 700), (4, '2024-02-01', 0, 700, 700), (4, '2024-03-01', 0, 700, 700),
(5, '2024-01-01', 4133, 2067, 6200), (5, '2024-02-01', 4133, 2067, 6200), (5, '2024-03-01', 4133, 2067, 6200),
(6, '2024-01-01', 0, 0, 0), (6, '2024-02-01', 0, 0, 0), (6, '2024-03-01', 0, 0, 0),
(7, '2024-01-01', 1200, 600, 1800), (7, '2024-02-01', 1200, 600, 1800), (7, '2024-03-01', 1200, 600, 1800),
(8, '2024-01-01', 3000, 1500, 4500), (8, '2024-02-01', 3000, 1500, 4500), (8, '2024-03-01', 3000, 1500, 4500),
(9, '2024-01-01', 600, 300, 900), (9, '2024-02-01', 600, 300, 900), (9, '2024-03-01', 600, 300, 900),
(10, '2024-01-01', 4667, 2333, 7000), (10, '2024-02-01', 4667, 2333, 7000), (10, '2024-03-01', 4667, 2333, 7000),
(11, '2024-01-01', 0, 0, 0), (11, '2024-02-01', 0, 0, 0), (11, '2024-03-01', 0, 0, 0),
(12, '2024-01-01', 2533, 1267, 3800), (12, '2024-02-01', 2533, 1267, 3800), (12, '2024-03-01', 2533, 1267, 3800),
(13, '2024-01-01', 5200, 2600, 7800), (13, '2024-02-01', 5200, 2600, 7800), (13, '2024-03-01', 5200, 2600, 7800),
(14, '2024-01-01', 0, 0, 0), (14, '2024-02-01', 0, 0, 0), (14, '2024-03-01', 0, 0, 0),
(15, '2024-01-01', 2133, 1067, 3200), (15, '2024-02-01', 2133, 1067, 3200), (15, '2024-03-01', 2133, 1067, 3200),
(16, '2024-01-01', 0, 500, 500), (16, '2024-02-01', 0, 500, 500), (16, '2024-03-01', 0, 500, 500),
(17, '2024-01-01', 4333, 2167, 6500), (17, '2024-02-01', 4333, 2167, 6500), (17, '2024-03-01', 4333, 2167, 6500),
(18, '2024-01-01', 0, 0, 0), (18, '2024-02-01', 0, 0, 0), (18, '2024-03-01', 0, 0, 0),
(19, '2024-01-01', 2833, 1417, 4250), (19, '2024-02-01', 2833, 1417, 4250), (19, '2024-03-01', 2833, 1417, 4250),
(20, '2024-01-01', 567, 283, 850), (20, '2024-02-01', 567, 283, 850), (20, '2024-03-01', 567, 283, 850),
(21, '2024-01-01', 5467, 2733, 8200), (21, '2024-02-01', 5467, 2733, 8200), (21, '2024-03-01', 5467, 2733, 8200),
(22, '2024-01-01', 0, 0, 0), (22, '2024-02-01', 0, 0, 0), (22, '2024-03-01', 0, 0, 0),
(23, '2024-01-01', 1133, 567, 1700), (23, '2024-02-01', 1133, 567, 1700), (23, '2024-03-01', 1133, 567, 1700),
(24, '2024-01-01', 3267, 1633, 4900), (24, '2024-02-01', 3267, 1633, 4900), (24, '2024-03-01', 3267, 1633, 4900),
(25, '2024-01-01', 667, 333, 1000), (25, '2024-02-01', 667, 333, 1000), (25, '2024-03-01', 667, 333, 1000),
(26, '2024-01-01', 2600, 1300, 3900), (26, '2024-02-01', 2600, 1300, 3900), (26, '2024-03-01', 2600, 1300, 3900),
(27, '2024-01-01', 0, 700, 700), (27, '2024-02-01', 0, 700, 700), (27, '2024-03-01', 0, 700, 700);


-- ============================================================
-- BENEFICIARIES
-- ============================================================

INSERT INTO beneficiaries (
    customer_id,
    full_name,
    relation,
    percentage,
    is_primary
)
VALUES
(1, 'Thomas Larsen', 'Ægtefælle', 100, 1),
(2, 'Mads Jensen', 'Samlever', 100, 1),
(3, 'Emma Nielsen', 'Barn', 50, 1),
(3, 'Lucas Nielsen', 'Barn', 50, 0),
(4, 'Nærmeste pårørende', 'Standard', 100, 1),
(5, 'Martin Pedersen', 'Ægtefælle', 100, 1),
(6, 'Sofie Madsen', 'Barn', 50, 1),
(6, 'Oliver Madsen', 'Barn', 50, 0),
(7, 'Nærmeste pårørende', 'Standard', 100, 1),
(8, 'Lene Andersen', 'Ægtefælle', 100, 1),
(9, 'Nærmeste pårørende', 'Standard', 100, 1),
(10, 'Freja Thomsen', 'Barn', 50, 1),
(10, 'Mikkel Thomsen', 'Barn', 50, 0),
(11, 'Nærmeste pårørende', 'Standard', 100, 1),
(12, 'Birgit Poulsen', 'Ægtefælle', 100, 1),
(13, 'Nærmeste pårørende', 'Standard', 100, 1),
(14, 'Sara Lund', 'Ægtefælle', 100, 1),
(15, 'Nærmeste pårørende', 'Standard', 100, 1);

