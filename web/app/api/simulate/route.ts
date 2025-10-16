export async function POST(request: Request) {
  try {
    const body = await request.json();

    const response = await fetch('http://localhost:8080/api/v1/simulate/montecarlo', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return Response.json(data);
  } catch {
    return Response.json({ error: 'Failed to run simulation' }, { status: 500 });
  }
}
