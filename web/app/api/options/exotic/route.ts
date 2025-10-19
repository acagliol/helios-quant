import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = await runExotic(body);
    return NextResponse.json(result);
  } catch (error) {
    console.error('Exotic option calculation error:', error);
    return NextResponse.json(
      { error: 'Calculation failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

function runExotic(params: any): Promise<{ price: number }> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), '..', 'scripts', 'exotic_api.py');
    const pythonPath = path.join(process.cwd(), '..', 'venv', 'bin', 'python');

    const pythonProcess = spawn(pythonPath, [pythonScript, JSON.stringify(params)]);

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
