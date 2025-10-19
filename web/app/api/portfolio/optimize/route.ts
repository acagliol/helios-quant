import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      n_assets = 10,
      risk_free_rate = 0.02,
      method = 'all'
    } = body

    const scriptPath = path.join(process.cwd(), '..', 'scripts', 'portfolio_optimize_api.py')
    const pythonPath = path.join(process.cwd(), '..', 'venv', 'bin', 'python')

    const params = JSON.stringify({
      n_assets,
      risk_free_rate,
      method
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
              { error: `Optimization failed: ${errorData}` },
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
                { error: 'Failed to parse optimization result' },
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
