export async function GET() {
  try {
    const response = await fetch('http://localhost:8080/api/v1/health');
    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    return Response.json({ status: 'offline' }, { status: 500 });
  }
}
