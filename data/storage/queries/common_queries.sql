-- Helios Quant Framework - Common SQL Queries

-- 1. Portfolio Performance Summary
SELECT
    fund_name,
    vintage,
    sector,
    committed_capital / 1000000.0 as committed_mm,
    current_nav / 1000000.0 as nav_mm,
    irr * 100 as irr_pct,
    moic,
    tvpi,
    dpi,
    sharpe_ratio,
    status
FROM portfolio_data
ORDER BY irr DESC;

-- 2. Sector Analysis
SELECT
    sector,
    COUNT(*) as num_funds,
    ROUND(AVG(irr) * 100, 2) as avg_irr_pct,
    ROUND(AVG(moic), 2) as avg_moic,
    ROUND(AVG(sharpe_ratio), 2) as avg_sharpe,
    ROUND(SUM(committed_capital) / 1000000.0, 2) as total_committed_mm,
    ROUND(SUM(current_nav) / 1000000.0, 2) as total_nav_mm
FROM portfolio_data
WHERE status = 'Active'
GROUP BY sector
ORDER BY avg_irr_pct DESC;

-- 3. Vintage Year Performance
SELECT
    vintage,
    COUNT(*) as num_funds,
    ROUND(AVG(irr) * 100, 2) as avg_irr_pct,
    ROUND(AVG(moic), 2) as avg_moic,
    ROUND(AVG(tvpi), 2) as avg_tvpi,
    ROUND(AVG(dpi), 2) as avg_dpi
FROM portfolio_data
GROUP BY vintage
ORDER BY vintage DESC;

-- 4. Top Performing Funds
SELECT
    fund_name,
    sector,
    vintage,
    ROUND(irr * 100, 2) as irr_pct,
    ROUND(moic, 2) as moic,
    ROUND(sharpe_ratio, 2) as sharpe,
    ROUND(current_nav / committed_capital, 2) as nav_multiple
FROM portfolio_data
WHERE status = 'Active'
ORDER BY irr DESC
LIMIT 10;

-- 5. Cash Flow Analysis by Fund
SELECT
    p.fund_name,
    cf.flow_type,
    COUNT(*) as num_transactions,
    ROUND(SUM(cf.amount) / 1000000.0, 2) as total_amount_mm,
    MIN(cf.flow_date) as first_date,
    MAX(cf.flow_date) as last_date
FROM portfolio_data p
JOIN cash_flows cf ON p.fund_id = cf.fund_id
GROUP BY p.fund_name, cf.flow_type
ORDER BY p.fund_name, cf.flow_type;

-- 6. Risk-Adjusted Performance
SELECT
    fund_name,
    sector,
    ROUND(irr * 100, 2) as irr_pct,
    ROUND(volatility * 100, 2) as volatility_pct,
    ROUND(sharpe_ratio, 2) as sharpe,
    ROUND(sortino_ratio, 2) as sortino,
    ROUND(irr / volatility, 2) as risk_adjusted_return
FROM portfolio_data
WHERE status = 'Active' AND volatility > 0
ORDER BY sharpe_ratio DESC;

-- 7. Recent ML Predictions
SELECT
    p.fund_name,
    mp.model_name,
    mp.prediction_date,
    ROUND(mp.predicted_irr * 100, 2) as predicted_irr_pct,
    ROUND(mp.confidence_lower * 100, 2) as lower_bound_pct,
    ROUND(mp.confidence_upper * 100, 2) as upper_bound_pct,
    mp.model_version
FROM ml_predictions mp
JOIN portfolio_data p ON mp.fund_id = p.fund_id
WHERE mp.prediction_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY mp.prediction_date DESC;

-- 8. Monte Carlo Simulation Results
SELECT
    p.fund_name,
    sr.simulation_type,
    sr.run_date,
    sr.iterations,
    ROUND(sr.mean_result * 100, 2) as mean_return_pct,
    ROUND(sr.std_dev * 100, 2) as std_dev_pct,
    ROUND(sr.percentile_5 * 100, 2) as p5_pct,
    ROUND(sr.percentile_95 * 100, 2) as p95_pct
FROM simulation_results sr
LEFT JOIN portfolio_data p ON sr.fund_id = p.fund_id
ORDER BY sr.run_date DESC
LIMIT 20;

-- 9. Portfolio Optimization Results
SELECT
    optimization_name,
    optimization_date,
    objective,
    ROUND(target_return * 100, 2) as target_return_pct,
    ROUND(portfolio_volatility * 100, 2) as volatility_pct,
    ROUND(sharpe_ratio, 2) as sharpe,
    weights
FROM optimization_results
ORDER BY optimization_date DESC
LIMIT 10;

-- 10. Analytics Jobs Status
SELECT
    job_name,
    job_type,
    status,
    started_at,
    completed_at,
    EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds
FROM analytics_jobs
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;

-- 11. Correlation Between Funds (requires multiple queries or window functions)
WITH fund_returns AS (
    SELECT
        fund_id,
        fund_name,
        irr,
        volatility
    FROM portfolio_data
    WHERE status = 'Active'
)
SELECT
    f1.fund_name as fund_1,
    f2.fund_name as fund_2,
    ROUND(f1.irr * 100, 2) as fund1_irr_pct,
    ROUND(f2.irr * 100, 2) as fund2_irr_pct
FROM fund_returns f1
CROSS JOIN fund_returns f2
WHERE f1.fund_id < f2.fund_id
ORDER BY ABS(f1.irr - f2.irr);

-- 12. Portfolio Concentration by Sector
SELECT
    sector,
    COUNT(*) as num_funds,
    ROUND(SUM(current_nav) / (SELECT SUM(current_nav) FROM portfolio_data WHERE status = 'Active') * 100, 2) as nav_concentration_pct,
    ROUND(SUM(committed_capital) / (SELECT SUM(committed_capital) FROM portfolio_data WHERE status = 'Active') * 100, 2) as committed_concentration_pct
FROM portfolio_data
WHERE status = 'Active'
GROUP BY sector
ORDER BY nav_concentration_pct DESC;

-- 13. Fund Performance vs Benchmark
SELECT
    fund_name,
    sector,
    ROUND(irr * 100, 2) as fund_irr_pct,
    ROUND(benchmark_return * 100, 2) as benchmark_return_pct,
    ROUND((irr - benchmark_return) * 100, 2) as alpha_pct,
    ROUND(beta, 2) as beta,
    CASE
        WHEN irr > benchmark_return THEN 'Outperforming'
        ELSE 'Underperforming'
    END as performance_status
FROM portfolio_data
WHERE status = 'Active' AND benchmark_return IS NOT NULL
ORDER BY (irr - benchmark_return) DESC;

-- 14. Recent Risk Metrics
SELECT
    p.fund_name,
    rm.metric_date,
    ROUND(rm.var_95 * 100, 2) as var_95_pct,
    ROUND(rm.cvar_95 * 100, 2) as cvar_95_pct,
    ROUND(rm.max_drawdown * 100, 2) as max_dd_pct,
    ROUND(rm.volatility * 100, 2) as volatility_pct,
    ROUND(rm.skewness, 2) as skewness,
    ROUND(rm.kurtosis, 2) as kurtosis
FROM risk_metrics rm
JOIN portfolio_data p ON rm.fund_id = p.fund_id
WHERE rm.metric_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY rm.metric_date DESC, p.fund_name;

-- 15. Cash Flow Timeline
SELECT
    p.fund_name,
    cf.flow_date,
    cf.flow_type,
    ROUND(cf.amount / 1000000.0, 2) as amount_mm,
    cf.description,
    SUM(cf.amount) OVER (PARTITION BY p.fund_id ORDER BY cf.flow_date) / 1000000.0 as cumulative_mm
FROM cash_flows cf
JOIN portfolio_data p ON cf.fund_id = p.fund_id
ORDER BY cf.flow_date DESC
LIMIT 50;
