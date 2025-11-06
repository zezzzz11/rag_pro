import { NextRequest, NextResponse } from 'next/server';
import { BACKEND_URL } from '@/lib/config';

export async function GET(request: NextRequest) {
  try {
    const authorization = request.headers.get('authorization');

    const response = await fetch(`${BACKEND_URL}/admin/users`, {
      method: 'GET',
      headers: {
        'Authorization': authorization || '',
      },
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: 'Failed to fetch users' },
      { status: 500 }
    );
  }
}
