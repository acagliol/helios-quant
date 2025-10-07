# Helios Quant Framework - Portfolio Analysis Module
# Statistical analysis and performance metrics for portfolio data

library(quantmod)
library(PerformanceAnalytics)
library(jsonlite)
library(DBI)
library(RPostgres)

# Database connection
connect_db <- function() {
  db_url <- Sys.getenv("DATABASE_URL", "postgres://localhost/helios_quant")
  con <- dbConnect(RPostgres::Postgres(), db_url)
  return(con)
}

# Load portfolio data from database
load_portfolio_data <- function(con) {
  query <- "SELECT * FROM portfolio_data ORDER BY fund_id"
  data <- dbGetQuery(con, query)
  return(data)
}

# Calculate Sharpe Ratio
calculate_sharpe <- function(returns, rf_rate = 0.02) {
  excess_returns <- returns - rf_rate / 252
  sharpe <- mean(excess_returns) / sd(excess_returns) * sqrt(252)
  return(sharpe)
}

# Calculate Sortino Ratio
calculate_sortino <- function(returns, rf_rate = 0.02, target = 0) {
  excess_returns <- returns - rf_rate / 252
  downside_returns <- returns[returns < target]
  downside_deviation <- sd(downside_returns)
  sortino <- mean(excess_returns) / downside_deviation * sqrt(252)
  return(sortino)
}

# CAPM Beta calculation
calculate_beta <- function(asset_returns, market_returns) {
  model <- lm(asset_returns ~ market_returns)
  beta <- coef(model)[2]
  return(beta)
}

# Calculate portfolio metrics
analyze_portfolio <- function(portfolio_data) {
  metrics <- list()

  for (i in 1:nrow(portfolio_data)) {
    fund <- portfolio_data[i, ]

    # Calculate alpha (excess return over benchmark)
    alpha <- fund$irr - fund$benchmark_return

    # Information ratio
    tracking_error <- abs(fund$irr - fund$benchmark_return) * 0.1
    info_ratio <- alpha / tracking_error

    # Risk-adjusted return
    risk_adjusted_return <- fund$irr / fund$volatility

    metrics[[i]] <- list(
      fund_id = fund$fund_id,
      sector = fund$sector,
      alpha = alpha,
      information_ratio = info_ratio,
      risk_adjusted_return = risk_adjusted_return,
      sharpe_estimate = fund$irr / fund$volatility
    )
  }

  return(metrics)
}

# Export results to JSON
export_results <- function(metrics, output_file = "r/output/portfolio_metrics.json") {
  json_data <- toJSON(metrics, pretty = TRUE, auto_unbox = TRUE)
  write(json_data, file = output_file)
  cat("Results exported to:", output_file, "\n")
}

# Main execution
main <- function() {
  tryCatch({
    con <- connect_db()

    # Load data
    portfolio_data <- load_portfolio_data(con)
    cat("Loaded", nrow(portfolio_data), "portfolio records\n")

    # Analyze portfolio
    metrics <- analyze_portfolio(portfolio_data)

    # Export results
    dir.create("r/output", showWarnings = FALSE, recursive = TRUE)
    export_results(metrics)

    # Print summary
    cat("\n=== Portfolio Analysis Summary ===\n")
    for (m in metrics) {
      cat(sprintf("Fund %d (%s): Alpha=%.2f%%, IR=%.2f, Risk-Adj Return=%.2f\n",
                  m$fund_id, m$sector, m$alpha * 100, m$information_ratio,
                  m$risk_adjusted_return))
    }

    dbDisconnect(con)

  }, error = function(e) {
    cat("Error in portfolio analysis:", conditionMessage(e), "\n")
  })
}

# Run if executed as script
if (!interactive()) {
  main()
}
