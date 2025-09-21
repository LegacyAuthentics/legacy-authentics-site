import { NextRequest, NextResponse } from 'next/server';

/**
 * Basic verification endpoint. In production, this would look up the
 * provided code in a database or ledger to confirm authenticity.
 */
export async function GET(req: NextRequest) {
  const code = req.nextUrl.searchParams.get('code');
  // Demo logic: Only a specific code is considered valid
  if (code === 'VALID123') {
    return NextResponse.json({ valid: true, issuedAt: '2024-01-01' });
  }
  return NextResponse.json({ valid: false });
}
