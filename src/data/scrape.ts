import { createScraper, ScraperScrapingResult } from "israeli-bank-scrapers";
import { AccountConfig } from "../types.js";
import { ScraperErrorTypes } from "israeli-bank-scrapers/lib/scrapers/errors.js";
import { createLogger } from "../utils/logger.js";
import { getFailureScreenShotPath } from "../utils/failureScreenshot.js";

const logger = createLogger("scrape");

export async function getAccountTransactions(
  account: AccountConfig,
  startDate: Date,
  futureMonthsToScrape: number,
  onProgress: (companyId: string, status: string) => void,
): Promise<ScraperScrapingResult> {
  logger(`started`);
  try {
    const scraper = createScraper({
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined,
      startDate,
      companyId: account.companyId,
      defaultTimeout: 180000,
      args: ["--disable-dev-shm-usage", "--no-sandbox"],
      futureMonthsToScrape: Number.isNaN(futureMonthsToScrape)
        ? undefined
        : futureMonthsToScrape,
      storeFailureScreenShotPath: getFailureScreenShotPath(account.companyId),
    });

    scraper.onProgress((companyId, { type }) => {
      logger(`[${companyId}] ${type}`);
      onProgress(companyId, type);
    });

    const result = await scraper.scrape(account);

    if (!result.success) {
      logger(`error: ${result.errorType} ${result.errorMessage}`);
    }
    logger(`ended`);

    return result;
  } catch (e) {
    logger(e);
    return {
      success: false,
      errorType: ScraperErrorTypes.Generic,
      errorMessage: String(e),
    };
  }
}
