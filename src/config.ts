import "dotenv/config";
import {
  subDays,
  format,
  startOfMonth,
  differenceInDays,
  startOfDay,
} from "date-fns";
import { AccountConfig, ScraperConfig } from "./types.js";
import { createLogger, logToPublicLog } from "./utils/logger.js";

export const systemName = "moneyman";
const logger = createLogger("config");

logger("Parsing config");
logToPublicLog("Parsing config");

const {
  DAYS_BACK,
  ACCOUNTS_JSON,
  TELEGRAM_API_KEY = "",
  TELEGRAM_CHAT_ID = "",
  GOOGLE_SHEET_ID = "",
  WORKSHEET_NAME,
  ACCOUNTS_TO_SCRAPE = "",
  FUTURE_MONTHS = "",
  SCRAPE_FROM_BEGINNING_OF_MONTH = "",
  TRANSACTION_HASH_TYPE = "",
  WEB_POST_URL = "",
  MAX_PARALLEL_SCRAPERS = "",
} = process.env;

/**
 * Add default values in case the value is falsy (0 is not valid here) or an empty string
 */
export const daysBackToScrape =
  SCRAPE_FROM_BEGINNING_OF_MONTH === "true"
    ? differenceInDays(Date.now(), startOfMonth(Date.now()))
    : DAYS_BACK || 10;
export const worksheetName = WORKSHEET_NAME || "_moneyman";
export const futureMonthsToScrape = parseInt(FUTURE_MONTHS, 10);
export const systemTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;


logger("Env", {
  systemName,
  systemTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
});

logger("env vars", {
  DAYS_BACK,
  ACCOUNTS_TO_SCRAPE,
  FUTURE_MONTHS,
  MAX_PARALLEL_SCRAPERS,
});

export {
  TELEGRAM_API_KEY,
  TELEGRAM_CHAT_ID,
  GOOGLE_SHEET_ID,
  TRANSACTION_HASH_TYPE,
  WEB_POST_URL,
};

export const currentDate = format(Date.now(), "yyyy-MM-dd");
export const scrapeStartDate =
  SCRAPE_FROM_BEGINNING_OF_MONTH === "true"
    ? startOfDay(
        subDays(
          Date.now(),
          Number(differenceInDays(Date.now(), startOfMonth(Date.now()))),
        ),
      )
    : startOfDay(subDays(Date.now(), Number(daysBackToScrape)));
function getAccounts(): Array<AccountConfig> {
  function parseAccounts(accountsJson?: string): Array<AccountConfig> {
    try {
      const parsed = JSON.parse(accountsJson!);
      if (Array.isArray(parsed)) {
        // TODO: Add schema validations?
        return parsed as Array<AccountConfig>;
      }
    } catch {}

    throw new TypeError("ACCOUNTS_JSON must be a valid array");
  }

  const allAccounts = parseAccounts(process.env.ACCOUNTS_JSON);
  const accountsToScrape = ACCOUNTS_TO_SCRAPE.split(",")
    .filter(Boolean)
    .map((a) => a.trim());

  return accountsToScrape.length == 0
    ? allAccounts
    : allAccounts.filter((account) =>
        accountsToScrape.includes(account.companyId),
      );
}

export const scraperConfig: ScraperConfig = {
  accounts: getAccounts(),
  startDate: subDays(Date.now(), Number(DAYS_BACK || 10)),
  parallelScrapers: Number(MAX_PARALLEL_SCRAPERS) || 1,
  futureMonthsToScrape: parseInt(FUTURE_MONTHS, 10),
};
