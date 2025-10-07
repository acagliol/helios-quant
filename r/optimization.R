# Helios Quant Framework - Portfolio Optimization Module
# Markowitz Mean-Variance Optimization and Efficient Frontier

library(quadprog)
library(ggplot2)
library(jsonlite)

# Mean-Variance Optimization (Markowitz)
markowitz_optimization <- function(expected_returns, cov_matrix, target_return = NULL) {
  n_assets <- length(expected_returns)

  # Constraint matrices
  # Amat: constraints (budget + target return if specified)
  # bvec: constraint values

  if (is.null(target_return)) {
    # Minimize variance subject to budget constraint only
    Dmat <- 2 * cov_matrix
    dvec <- rep(0, n_assets)
    Amat <- cbind(rep(1, n_assets), diag(n_assets))
    bvec <- c(1, rep(0, n_assets))

    result <- solve.QP(Dmat, dvec, Amat, bvec, meq = 1)
  } else {
    # Minimize variance for target return
    Dmat <- 2 * cov_matrix
    dvec <- rep(0, n_assets)
    Amat <- cbind(rep(1, n_assets), expected_returns, diag(n_assets))
    bvec <- c(1, target_return, rep(0, n_assets))

    result <- solve.QP(Dmat, dvec, Amat, bvec, meq = 2)
  }

  weights <- result$solution
  names(weights) <- names(expected_returns)

  portfolio_return <- sum(weights * expected_returns)
  portfolio_variance <- t(weights) %*% cov_matrix %*% weights
  portfolio_volatility <- sqrt(portfolio_variance)

  return(list(
    weights = weights,
    expected_return = as.numeric(portfolio_return),
    volatility = as.numeric(portfolio_volatility),
    sharpe_ratio = as.numeric(portfolio_return / portfolio_volatility)
  ))
}

# Generate Efficient Frontier
efficient_frontier <- function(expected_returns, cov_matrix, n_portfolios = 100) {
  min_return <- min(expected_returns)
  max_return <- max(expected_returns)
  target_returns <- seq(min_return, max_return, length.out = n_portfolios)

  frontier <- data.frame(
    return = numeric(n_portfolios),
    volatility = numeric(n_portfolios),
    sharpe = numeric(n_portfolios)
  )

  for (i in 1:n_portfolios) {
    tryCatch({
      opt <- markowitz_optimization(expected_returns, cov_matrix, target_returns[i])
      frontier[i, "return"] <- opt$expected_return
      frontier[i, "volatility"] <- opt$volatility
      frontier[i, "sharpe"] <- opt$sharpe_ratio
    }, error = function(e) {
      frontier[i, ] <- NA
    })
  }

  # Remove failed optimizations
  frontier <- na.omit(frontier)

  return(frontier)
}

# Plot Efficient Frontier
plot_efficient_frontier <- function(frontier, output_file = "r/output/efficient_frontier.png") {
  # Create plot
  p <- ggplot(frontier, aes(x = volatility * 100, y = return * 100)) +
    geom_line(color = "blue", size = 1.2) +
    geom_point(aes(color = sharpe), size = 2) +
    scale_color_gradient(low = "red", high = "green", name = "Sharpe Ratio") +
    labs(
      title = "Efficient Frontier - Mean-Variance Optimization",
      x = "Portfolio Volatility (%)",
      y = "Expected Return (%)",
      caption = "Helios Quant Framework"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
      legend.position = "right"
    )

  # Save plot
  dir.create("r/output", showWarnings = FALSE, recursive = TRUE)
  ggsave(output_file, p, width = 10, height = 6, dpi = 300)
  cat("Efficient frontier plot saved to:", output_file, "\n")

  return(p)
}

# Maximum Sharpe Ratio Portfolio
max_sharpe_portfolio <- function(expected_returns, cov_matrix, rf_rate = 0.02) {
  n_assets <- length(expected_returns)

  # Objective: maximize Sharpe = (Return - Rf) / Volatility
  # Equivalent to: minimize -Sharpe

  excess_returns <- expected_returns - rf_rate

  # Use optimization to find max Sharpe
  objective <- function(weights) {
    portfolio_return <- sum(weights * expected_returns)
    portfolio_variance <- t(weights) %*% cov_matrix %*% weights
    portfolio_volatility <- sqrt(portfolio_variance)
    sharpe <- -(portfolio_return - rf_rate) / portfolio_volatility
    return(sharpe)
  }

  # Constraints: weights sum to 1, all weights >= 0
  result <- optim(
    par = rep(1/n_assets, n_assets),
    fn = objective,
    method = "L-BFGS-B",
    lower = rep(0, n_assets),
    upper = rep(1, n_assets)
  )

  weights <- result$par / sum(result$par)  # Normalize
  names(weights) <- names(expected_returns)

  portfolio_return <- sum(weights * expected_returns)
  portfolio_variance <- t(weights) %*% cov_matrix %*% weights
  portfolio_volatility <- sqrt(portfolio_variance)

  return(list(
    weights = weights,
    expected_return = as.numeric(portfolio_return),
    volatility = as.numeric(portfolio_volatility),
    sharpe_ratio = as.numeric((portfolio_return - rf_rate) / portfolio_volatility)
  ))
}

# Example execution
run_optimization <- function() {
  # Sample data: 5 assets
  set.seed(42)
  n_assets <- 5
  asset_names <- paste0("Asset_", 1:n_assets)

  expected_returns <- rnorm(n_assets, mean = 0.08, sd = 0.03)
  names(expected_returns) <- asset_names

  # Create covariance matrix
  volatilities <- runif(n_assets, 0.15, 0.30)
  correlation <- matrix(0.3, n_assets, n_assets)
  diag(correlation) <- 1
  cov_matrix <- diag(volatilities) %*% correlation %*% diag(volatilities)
  rownames(cov_matrix) <- colnames(cov_matrix) <- asset_names

  # Find maximum Sharpe portfolio
  max_sharpe <- max_sharpe_portfolio(expected_returns, cov_matrix)

  cat("\n=== Maximum Sharpe Ratio Portfolio ===\n")
  cat(sprintf("Expected Return: %.2f%%\n", max_sharpe$expected_return * 100))
  cat(sprintf("Volatility: %.2f%%\n", max_sharpe$volatility * 100))
  cat(sprintf("Sharpe Ratio: %.2f\n", max_sharpe$sharpe_ratio))
  cat("\nOptimal Weights:\n")
  print(round(max_sharpe$weights * 100, 2))

  # Generate efficient frontier
  frontier <- efficient_frontier(expected_returns, cov_matrix, 50)

  # Plot
  plot_efficient_frontier(frontier)

  # Export results
  dir.create("r/output", showWarnings = FALSE, recursive = TRUE)
  results <- list(
    max_sharpe_portfolio = max_sharpe,
    efficient_frontier = frontier
  )
  json_data <- toJSON(results, pretty = TRUE, auto_unbox = TRUE)
  write(json_data, "r/output/optimization_results.json")

  return(results)
}

# Run if executed as script
if (!interactive()) {
  run_optimization()
}
