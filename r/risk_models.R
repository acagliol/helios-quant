# Helios Quant Framework - Risk Models Module
# CAPM, VaR, and risk decomposition analysis

library(quantmod)
library(PerformanceAnalytics)
library(jsonlite)

# Value at Risk (VaR) calculation
calculate_var <- function(returns, confidence = 0.95, method = "historical") {
  if (method == "historical") {
    var <- quantile(returns, 1 - confidence)
  } else if (method == "parametric") {
    mu <- mean(returns)
    sigma <- sd(returns)
    var <- qnorm(1 - confidence, mean = mu, sd = sigma)
  }
  return(var)
}

# Conditional Value at Risk (CVaR/ES)
calculate_cvar <- function(returns, confidence = 0.95) {
  var <- calculate_var(returns, confidence, "historical")
  cvar <- mean(returns[returns <= var])
  return(cvar)
}

# Maximum Drawdown
calculate_max_drawdown <- function(returns) {
  cumulative <- cumprod(1 + returns)
  running_max <- cummax(cumulative)
  drawdown <- (cumulative - running_max) / running_max
  max_dd <- min(drawdown)
  return(max_dd)
}

# CAPM Analysis
capm_analysis <- function(asset_returns, market_returns, rf_rate = 0.02) {
  excess_asset <- asset_returns - rf_rate / 252
  excess_market <- market_returns - rf_rate / 252

  model <- lm(excess_asset ~ excess_market)

  alpha <- coef(model)[1] * 252  # Annualized
  beta <- coef(model)[2]
  r_squared <- summary(model)$r.squared

  return(list(
    alpha = alpha,
    beta = beta,
    r_squared = r_squared,
    residual_volatility = sd(residuals(model)) * sqrt(252)
  ))
}

# Portfolio risk decomposition
risk_decomposition <- function(portfolio_weights, cov_matrix) {
  portfolio_variance <- t(portfolio_weights) %*% cov_matrix %*% portfolio_weights
  portfolio_volatility <- sqrt(portfolio_variance)

  # Marginal contribution to risk
  marginal_contrib <- (cov_matrix %*% portfolio_weights) / as.numeric(portfolio_volatility)

  # Component contribution to risk
  component_contrib <- portfolio_weights * marginal_contrib

  return(list(
    total_volatility = as.numeric(portfolio_volatility),
    marginal_contribution = as.vector(marginal_contrib),
    component_contribution = as.vector(component_contrib),
    percentage_contribution = as.vector(component_contrib / portfolio_volatility * 100)
  ))
}

# Simulate correlated returns
simulate_correlated_returns <- function(n_assets, n_periods, mu, sigma, correlation) {
  # Create correlation matrix
  corr_matrix <- matrix(correlation, n_assets, n_assets)
  diag(corr_matrix) <- 1

  # Covariance matrix
  cov_matrix <- diag(sigma) %*% corr_matrix %*% diag(sigma)

  # Generate correlated normal returns
  returns <- MASS::mvrnorm(n = n_periods, mu = mu, Sigma = cov_matrix)

  return(returns)
}

# Risk metrics summary
calculate_risk_metrics <- function(returns) {
  metrics <- list(
    var_95 = calculate_var(returns, 0.95),
    var_99 = calculate_var(returns, 0.99),
    cvar_95 = calculate_cvar(returns, 0.95),
    cvar_99 = calculate_cvar(returns, 0.99),
    max_drawdown = calculate_max_drawdown(returns),
    volatility = sd(returns) * sqrt(252),
    skewness = moments::skewness(returns),
    kurtosis = moments::kurtosis(returns)
  )

  return(metrics)
}

# Example execution
run_risk_analysis <- function() {
  # Simulate sample data
  set.seed(42)
  n_periods <- 252
  returns <- rnorm(n_periods, mean = 0.0005, sd = 0.015)

  # Calculate risk metrics
  risk_metrics <- calculate_risk_metrics(returns)

  cat("\n=== Risk Analysis Results ===\n")
  cat(sprintf("VaR (95%%): %.2f%%\n", risk_metrics$var_95 * 100))
  cat(sprintf("VaR (99%%): %.2f%%\n", risk_metrics$var_99 * 100))
  cat(sprintf("CVaR (95%%): %.2f%%\n", risk_metrics$cvar_95 * 100))
  cat(sprintf("Max Drawdown: %.2f%%\n", risk_metrics$max_drawdown * 100))
  cat(sprintf("Volatility: %.2f%%\n", risk_metrics$volatility * 100))

  # Export results
  dir.create("r/output", showWarnings = FALSE, recursive = TRUE)
  json_data <- toJSON(risk_metrics, pretty = TRUE, auto_unbox = TRUE)
  write(json_data, "r/output/risk_metrics.json")

  return(risk_metrics)
}

# Run if executed as script
if (!interactive()) {
  run_risk_analysis()
}
