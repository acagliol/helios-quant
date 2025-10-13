package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"sort"
	"sync"
	"time"

	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
)

// PortfolioData represents fund performance data
type PortfolioData struct {
	FundID           int     `json:"fund_id"`
	Vintage          int     `json:"vintage"`
	Sector           string  `json:"sector"`
	CommittedCapital float64 `json:"committed_capital"`
	IRR              float64 `json:"irr"`
	BenchmarkReturn  float64 `json:"benchmark_return"`
	Volatility       float64 `json:"volatility"`
}

// SimulationResult holds Monte Carlo simulation output
type SimulationResult struct {
	Mean       float64   `json:"mean"`
	StdDev     float64   `json:"std_dev"`
	Percentile []float64 `json:"percentile"`
	Iterations int       `json:"iterations"`
}

var db *sql.DB

// CORS middleware
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func main() {
	// Initialize database connection
	var err error
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://localhost/helios_quant?sslmode=disable"
	}

	db, err = sql.Open("postgres", dbURL)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer db.Close()

	// Initialize router
	r := mux.NewRouter()

	// CORS middleware
	r.Use(corsMiddleware)

	// API routes
	r.HandleFunc("/api/v1/health", healthCheck).Methods("GET")
	r.HandleFunc("/api/v1/portfolio", getPortfolioData).Methods("GET")
	r.HandleFunc("/api/v1/simulate/montecarlo", runMonteCarloAPI).Methods("POST")
	r.HandleFunc("/api/v1/analytics/trigger", triggerAnalytics).Methods("POST")

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Helios Quant Framework API starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "healthy",
		"service": "Helios Quant Framework",
		"version": "1.0.0",
	})
}

func getPortfolioData(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query(`
		SELECT fund_id, vintage, sector, committed_capital,
		       irr, benchmark_return, volatility
		FROM portfolio_data
		ORDER BY fund_id
	`)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var portfolios []PortfolioData
	for rows.Next() {
		var p PortfolioData
		err := rows.Scan(&p.FundID, &p.Vintage, &p.Sector, &p.CommittedCapital,
			&p.IRR, &p.BenchmarkReturn, &p.Volatility)
		if err != nil {
			log.Println("Error scanning row:", err)
			continue
		}
		portfolios = append(portfolios, p)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(portfolios)
}

func runMonteCarloAPI(w http.ResponseWriter, r *http.Request) {
	var params struct {
		Iterations int     `json:"iterations"`
		Mean       float64 `json:"mean"`
		StdDev     float64 `json:"std_dev"`
		Jobs       int     `json:"jobs"`
	}

	if err := json.NewDecoder(r.Body).Decode(&params); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if params.Iterations == 0 {
		params.Iterations = 10000
	}
	if params.Jobs == 0 {
		params.Jobs = 4
	}

	result := runMonteCarloSimulation(params.Iterations, params.Mean, params.StdDev, params.Jobs)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func triggerAnalytics(w http.ResponseWriter, r *http.Request) {
	// Trigger R and Python analytics via subprocess or API calls
	// This is a placeholder for orchestration logic

	response := map[string]interface{}{
		"status": "triggered",
		"jobs": []string{
			"R: Portfolio Optimization",
			"Python: ML Forecasting",
			"R: Risk Analysis",
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// runMonteCarloSimulation executes parallel Monte Carlo simulations
func runMonteCarloSimulation(iterations int, mean, stdDev float64, jobs int) SimulationResult {
	results := make([]float64, iterations)
	chunkSize := iterations / jobs
	var wg sync.WaitGroup

	for i := 0; i < jobs; i++ {
		wg.Add(1)
		start := i * chunkSize
		end := start + chunkSize
		if i == jobs-1 {
			end = iterations
		}

		go func(start, end int) {
			defer wg.Done()
			source := rand.NewSource(time.Now().UnixNano())
			rng := rand.New(source)

			for j := start; j < end; j++ {
				results[j] = simulatePortfolioReturn(mean, stdDev, rng)
			}
		}(start, end)
	}

	wg.Wait()

	// Calculate statistics
	return calculateStatistics(results)
}

// simulatePortfolioReturn generates a single portfolio return simulation
func simulatePortfolioReturn(mean, stdDev float64, rng *rand.Rand) float64 {
	// Box-Muller transform for normal distribution
	u1 := rng.Float64()
	u2 := rng.Float64()
	z := math.Sqrt(-2*math.Log(u1)) * math.Cos(2*math.Pi*u2)
	return mean + stdDev*z
}

// calculateStatistics computes summary statistics from simulation results
func calculateStatistics(results []float64) SimulationResult {
	n := float64(len(results))

	// Mean
	var sum float64
	for _, v := range results {
		sum += v
	}
	mean := sum / n

	// Standard deviation
	var variance float64
	for _, v := range results {
		variance += math.Pow(v-mean, 2)
	}
	stdDev := math.Sqrt(variance / n)

	// Percentiles
	sorted := make([]float64, len(results))
	copy(sorted, results)
	sort.Float64s(sorted)

	percentiles := []float64{
		sorted[int(0.05*n)], // 5th percentile
		sorted[int(0.25*n)], // 25th percentile
		sorted[int(0.50*n)], // 50th percentile (median)
		sorted[int(0.75*n)], // 75th percentile
		sorted[int(0.95*n)], // 95th percentile
	}

	return SimulationResult{
		Mean:       mean,
		StdDev:     stdDev,
		Percentile: percentiles,
		Iterations: len(results),
	}
}
