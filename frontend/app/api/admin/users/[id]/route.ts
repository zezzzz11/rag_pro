import { NextRequest, NextResponse } from 'next/server';
import { BACKEND_URL } from '@/lib/config';

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const authorization = request.headers.get('authorization');

    const response = await fetch(`${BACKEND_URL}/admin/users/${params.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': authorization || '',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: 'Failed to delete user' },
      { status: 500 }
    );
  }
}
