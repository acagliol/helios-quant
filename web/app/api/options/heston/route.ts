import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { S0, K, T, r, v0, kappa, theta, sigma, rho, q = 0 } = body;

    // Validate inputs
    if (!S0 || !K || !T || r === undefined || !v0 || !kappa || !theta || !sigma || rho === undefined) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Call Python Heston implementation
    const result = await runHeston({ S0, K, T, r, v0, kappa, theta, sigma, rho, q });

    return NextResponse.json(result);
  } catch (error) {
    console.error('Heston calculation error:', error);
    return NextResponse.json(
      { error: 'Calculation failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

function runHeston(params: {
  S0: number;
  K: number;
  T: number;
  r: number;
  v0: number;
  kappa: number;
  theta: number;
  sigma: number;
  rho: number;
  q: number;
}): Promise<{
  call_price: number;
  put_price: number;
  implied_vol: number;
}> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), '..', 'scripts', 'heston_api.py');
    const pythonPath = path.join(process.cwd(), '..', 'venv', 'bin', 'python');

    const pythonProcess = spawn(pythonPath, [
      pythonScript,
      params.S0.toString(),
      params.K.toString(),
      params.T.toString(),
      params.r.toString(),
      params.v0.toString(),
      params.kappa.toString(),
      params.theta.toString(),
      params.sigma.toString(),
      params.rho.toString(),
      params.q.toString()
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
