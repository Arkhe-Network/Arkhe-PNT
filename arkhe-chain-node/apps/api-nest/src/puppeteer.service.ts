import { Injectable } from '@nestjs/common';
import puppeteer from 'puppeteer';
import { logger } from '@arkhe/shared';
import * as path from 'path';

@Injectable()
export class PuppeteerService {
  async generateCoherenceReport(lambda: number): Promise<string> {
    const browser = await puppeteer.launch({
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    const page = await browser.newPage();

    const htmlContent = `
      <html>
        <head><style>body { font-family: sans-serif; }</style></head>
        <body>
          <h1>Arkhe-Chain Coherence Report</h1>
          <p>Global Coherence (λ₂): <strong>${lambda.toFixed(4)}</strong></p>
          <p>Timestamp: ${new Date().toISOString()}</p>
        </body>
      </html>
    `;

    await page.setContent(htmlContent);
    const pdfPath = path.join(process.cwd(), 'coherence_report.pdf');
    await page.pdf({ path: pdfPath, format: 'A4' });

    await browser.close();
    logger.info(`Puppeteer report generated: ${pdfPath}`);
    return pdfPath;
  }
}
