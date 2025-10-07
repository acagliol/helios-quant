package main

import (
	"math"
	"math/rand"
	"sort"
	"sync"
	"time"
)

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
