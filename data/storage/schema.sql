-- Helios Quant Framework - Database Schema
-- PostgreSQL schema for portfolio, market, and analytics data

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Portfolio data table
CREATE TABLE IF NOT EXISTS portfolio_data (
    fund_id SERIAL PRIMARY KEY,
    fund_name VARCHAR(255) NOT NULL,
    vintage INT NOT NULL,
    sector VARCHAR(100) NOT NULL,
    committed_capital NUMERIC(15, 2) NOT NULL,
    invested_capital NUMERIC(15, 2) DEFAULT 0,
    current_nav NUMERIC(15, 2),
    irr NUMERIC(8, 4),
    moic NUMERIC(8, 4),
    tvpi NUMERIC(8, 4),
    dpi NUMERIC(8, 4),
    rvpi NUMERIC(8, 4),
    benchmark_return NUMERIC(8, 4),
    volatility NUMERIC(8, 4),
    beta NUMERIC(8, 4),
    alpha NUMERIC(8, 4),
    sharpe_ratio NUMERIC(8, 4),
    sortino_ratio NUMERIC(8, 4),
    max_drawdown NUMERIC(8, 4),
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_vintage CHECK (vintage BETWEEN 1990 AND 2100),
    CONSTRAINT valid_status CHECK (status IN ('Active', 'Realized', 'Written-Off'))
);

-- Cash flows table
CREATE TABLE IF NOT EXISTS cash_flows (
    cash_flow_id SERIAL PRIMARY KEY,
    fund_id INT NOT NULL REFERENCES portfolio_data(fund_id) ON DELETE CASCADE,
    flow_date DATE NOT NULL,
    flow_type VARCHAR(50) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_flow_type CHECK (flow_type IN ('Capital Call', 'Distribution', 'Dividend', 'Interest', 'Fee', 'Other'))
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    market_data_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open_price NUMERIC(12, 4),
    high_price NUMERIC(12, 4),
    low_price NUMERIC(12, 4),
    close_price NUMERIC(12, 4),
    adj_close NUMERIC(12, 4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ticker, date)
);

-- Benchmark data table
CREATE TABLE IF NOT EXISTS benchmark_data (
    benchmark_id SERIAL PRIMARY KEY,
    benchmark_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    return_value NUMERIC(10, 6),
    index_level NUMERIC(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(benchmark_name, date)
);

-- Risk metrics table
CREATE TABLE IF NOT EXISTS risk_metrics (
    risk_metric_id SERIAL PRIMARY KEY,
    fund_id INT NOT NULL REFERENCES portfolio_data(fund_id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    var_95 NUMERIC(10, 6),
    var_99 NUMERIC(10, 6),
    cvar_95 NUMERIC(10, 6),
    cvar_99 NUMERIC(10, 6),
    max_drawdown NUMERIC(10, 6),
    volatility NUMERIC(10, 6),
    skewness NUMERIC(10, 6),
    kurtosis NUMERIC(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(fund_id, metric_date)
);

-- ML predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id SERIAL PRIMARY KEY,
    fund_id INT NOT NULL REFERENCES portfolio_data(fund_id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_irr NUMERIC(8, 4),
    confidence_lower NUMERIC(8, 4),
    confidence_upper NUMERIC(8, 4),
    model_version VARCHAR(50),
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Simulation results table
CREATE TABLE IF NOT EXISTS simulation_results (
    simulation_id SERIAL PRIMARY KEY,
    fund_id INT REFERENCES portfolio_data(fund_id) ON DELETE CASCADE,
    simulation_type VARCHAR(50) NOT NULL,
    run_date DATE NOT NULL,
    iterations INT NOT NULL,
    mean_result NUMERIC(12, 6),
    std_dev NUMERIC(12, 6),
    percentile_5 NUMERIC(12, 6),
    percentile_25 NUMERIC(12, 6),
    percentile_50 NUMERIC(12, 6),
    percentile_75 NUMERIC(12, 6),
    percentile_95 NUMERIC(12, 6),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_simulation_type CHECK (simulation_type IN ('Monte Carlo', 'Scenario Analysis', 'Stress Test'))
);

-- Portfolio optimization results table
CREATE TABLE IF NOT EXISTS optimization_results (
    optimization_id SERIAL PRIMARY KEY,
    optimization_name VARCHAR(255) NOT NULL,
    optimization_date DATE NOT NULL,
    objective VARCHAR(100) NOT NULL,
    target_return NUMERIC(8, 4),
    portfolio_volatility NUMERIC(8, 4),
    sharpe_ratio NUMERIC(8, 4),
    weights JSONB NOT NULL,
    constraints JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_objective CHECK (objective IN ('Min Variance', 'Max Sharpe', 'Max Return', 'Risk Parity'))
);

-- Analytics jobs table (for tracking R and Python job execution)
CREATE TABLE IF NOT EXISTS analytics_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    parameters JSONB,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_status CHECK (status IN ('Pending', 'Running', 'Completed', 'Failed')),
    CONSTRAINT valid_job_type CHECK (job_type IN ('R-Analysis', 'R-Optimization', 'R-Risk', 'Python-ML', 'Python-QuantLib', 'Go-Simulation'))
);

-- Create indexes for performance
CREATE INDEX idx_portfolio_vintage ON portfolio_data(vintage);
CREATE INDEX idx_portfolio_sector ON portfolio_data(sector);
CREATE INDEX idx_portfolio_status ON portfolio_data(status);
CREATE INDEX idx_cash_flows_fund_date ON cash_flows(fund_id, flow_date);
CREATE INDEX idx_market_data_ticker_date ON market_data(ticker, date);
CREATE INDEX idx_benchmark_name_date ON benchmark_data(benchmark_name, date);
CREATE INDEX idx_risk_metrics_fund_date ON risk_metrics(fund_id, metric_date);
CREATE INDEX idx_ml_predictions_fund_date ON ml_predictions(fund_id, prediction_date);
CREATE INDEX idx_analytics_jobs_status ON analytics_jobs(status);

-- Create views for common queries

-- Portfolio summary view
CREATE OR REPLACE VIEW vw_portfolio_summary AS
SELECT
    p.fund_id,
    p.fund_name,
    p.vintage,
    p.sector,
    p.committed_capital,
    p.invested_capital,
    p.current_nav,
    p.irr,
    p.moic,
    p.tvpi,
    p.dpi,
    p.sharpe_ratio,
    COUNT(cf.cash_flow_id) as num_cash_flows,
    SUM(CASE WHEN cf.flow_type = 'Distribution' THEN cf.amount ELSE 0 END) as total_distributions,
    SUM(CASE WHEN cf.flow_type = 'Capital Call' THEN cf.amount ELSE 0 END) as total_capital_calls
FROM portfolio_data p
LEFT JOIN cash_flows cf ON p.fund_id = cf.fund_id
GROUP BY p.fund_id;

-- Sector performance view
CREATE OR REPLACE VIEW vw_sector_performance AS
SELECT
    sector,
    COUNT(*) as num_funds,
    AVG(irr) as avg_irr,
    AVG(moic) as avg_moic,
    AVG(sharpe_ratio) as avg_sharpe,
    AVG(volatility) as avg_volatility,
    SUM(committed_capital) as total_committed,
    SUM(current_nav) as total_nav
FROM portfolio_data
WHERE status = 'Active'
GROUP BY sector;

-- Recent analytics jobs view
CREATE OR REPLACE VIEW vw_recent_analytics_jobs AS
SELECT
    job_id,
    job_name,
    job_type,
    status,
    started_at,
    completed_at,
    EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds,
    created_at
FROM analytics_jobs
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_portfolio_data_updated_at
    BEFORE UPDATE ON portfolio_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO portfolio_data (fund_name, vintage, sector, committed_capital, invested_capital, current_nav, irr, moic, tvpi, dpi, benchmark_return, volatility, status)
VALUES
    ('Tech Growth Fund I', 2018, 'Technology', 100000000, 95000000, 180000000, 0.2450, 1.89, 1.95, 0.50, 0.1200, 0.2800, 'Active'),
    ('Healthcare Ventures II', 2019, 'Healthcare', 75000000, 72000000, 115000000, 0.1850, 1.60, 1.72, 0.35, 0.0950, 0.2200, 'Active'),
    ('Energy Transition Fund', 2020, 'Energy', 150000000, 130000000, 195000000, 0.1650, 1.50, 1.63, 0.28, 0.0850, 0.3200, 'Active'),
    ('Consumer Brand Partners', 2017, 'Consumer', 50000000, 50000000, 92000000, 0.2150, 1.84, 2.10, 0.68, 0.1100, 0.2500, 'Active'),
    ('Fintech Innovation Fund', 2021, 'Finance', 200000000, 150000000, 210000000, 0.1250, 1.40, 1.48, 0.18, 0.1000, 0.3500, 'Active');

COMMENT ON TABLE portfolio_data IS 'Core portfolio fund data with performance metrics';
COMMENT ON TABLE cash_flows IS 'Cash flow transactions for each fund';
COMMENT ON TABLE market_data IS 'Historical market price data for benchmarking';
COMMENT ON TABLE risk_metrics IS 'Calculated risk metrics per fund';
COMMENT ON TABLE ml_predictions IS 'Machine learning model predictions';
COMMENT ON TABLE simulation_results IS 'Monte Carlo and scenario analysis results';
COMMENT ON TABLE optimization_results IS 'Portfolio optimization results from R models';
COMMENT ON TABLE analytics_jobs IS 'Tracking table for cross-language analytics job execution';
