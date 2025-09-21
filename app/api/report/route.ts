import { NextResponse } from 'next/server';
import { PDFDocument, StandardFonts } from 'pdf-lib';

/**
 * Creates a simple sample PDF report. In production, you would fetch
 * the analysis results and populate a template with detailed findings.
 */
export async function GET() {
  try {
    const pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([612, 792]); // Letter size (8.5 x 11 inches)
    const { width, height } = page.getSize();
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
    // Header
    const title = 'Sample Autograph Verification Report';
    const titleSize = 24;
    const titleWidth = font.widthOfTextAtSize(title, titleSize);
    page.drawText(title, {
      x: (width - titleWidth) / 2,
      y: height - 80,
      size: titleSize,
      font,
    });
    // Body text
    const body = 'This sample report illustrates the format of your certificate.\\n\\nYour authentic autograph will be thoroughly analyzed by our team of experts using forensic techniques. The report includes details about ink consistency, paper age, provenance, and comparative signature analysis.\\n\\nEach report is digitally signed and assigned a unique verification code. Third parties can confirm authenticity using our verification page.';
    const fontSize = 12;
    const lines = body.split('\\n');
    let y = height - 130;
    for (const line of lines) {
      page.drawText(line, {
        x: 50,
        y,
        size: fontSize,
        font,
        maxWidth: width - 100,
        lineHeight: fontSize * 1.4,
      });
      y -= fontSize * 1.4;
    }
    const pdfBytes = await pdfDoc.save();
    return new NextResponse(Buffer.from(pdfBytes), {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="sample-report.pdf"',
      },
    });
  } catch (error) {
    console.error(error);
    return new NextResponse('Failed to generate report', { status: 500 });
  }
}
