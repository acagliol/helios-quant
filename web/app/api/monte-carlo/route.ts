import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      S, K, T, r, sigma, option_type, q = 0.0,
      n_paths = 100000,
      variance_reduction = 'antithetic'
    } = body

    // Validate inputs
    if (!S || !K || !T || r === undefined || !sigma) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      )
    }

    const scriptPath = path.join(process.cwd(), '..', 'scripts', 'monte_carlo_api.py')
    const pythonPath = path.join(process.cwd(), '..', 'venv', 'bin', 'python')

    const params = JSON.stringify({
      S, K, T, r, sigma, option_type, q,
      n_paths, variance_reduction
    })

    return new Promise((resolve) => {
      const pythonProcess = spawn(pythonPath, [scriptPath, params])
      let outputData = ''
      let errorData = ''

      pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString()
      })

      pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString()
      })

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          resolve(
            NextResponse.json(
              { error: `Calculation failed: ${errorData}` },
              { status: 500 }
            )
          )
        } else {
          try {
            const result = JSON.parse(outputData)
            resolve(NextResponse.json(result))
          } catch (e) {
            resolve(
              NextResponse.json(
                { error: 'Failed to parse calculation result' },
                { status: 500 }
              )
            )
          }
        }
      })
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Server error' },
      { status: 500 }
    )
  }
}
