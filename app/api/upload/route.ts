import { NextResponse } from 'next/server';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const s3 = new S3Client({ region: process.env.AWS_REGION });

export async function POST() {
  const key = 'uploads/' + crypto.randomUUID();
  const command = new PutObjectCommand({
    Bucket: process.env.AWS_BUCKET_NAME!,
    Key: key,
    ContentType: 'application/octet-stream',
  });

  const uploadUrl = await getSignedUrl(s3, command, { expiresIn: 60 });
  return NextResponse.json({ uploadUrl });
}
