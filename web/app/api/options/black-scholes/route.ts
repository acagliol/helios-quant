import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { S, K, T, r, sigma, q = 0, option_type = 'call' } = body;

    // Validate inputs
    if (!S || !K || !T || r === undefined || !sigma) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Call Python Black-Scholes implementation
    const result = await runBlackScholes({ S, K, T, r, sigma, q, option_type });

    return NextResponse.json(result);
  } catch (error) {
    console.error('Black-Scholes calculation error:', error);
    return NextResponse.json(
      { error: 'Calculation failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

function runBlackScholes(params: {
  S: number;
  K: number;
  T: number;
  r: number;
  sigma: number;
  q: number;
  option_type: string;
}): Promise<{
  price: number;
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho: number;
}> {
  return new Promise((resolve, reject) => {
    // Path to Python script
    const pythonScript = path.join(process.cwd(), '..', 'scripts', 'black_scholes_api.py');

    // Use the virtual environment's Python
    const pythonPath = path.join(process.cwd(), '..', 'venv', 'bin', 'python');

    const pythonProcess = spawn(pythonPath, [
      pythonScript,
      params.S.toString(),
      params.K.toString(),
      params.T.toString(),
      params.r.toString(),
      params.sigma.toString(),
      params.q.toString(),
      params.option_type
    ]);

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`));
        return;
      }

      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse Python output: ${stdout}`));
      }
    });

    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
}
