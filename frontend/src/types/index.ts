export interface BalanceSheetData {
  symbol: string;
  date: string;
  reportedCurrency: string;
  cik: string;
  fillingDate: string;
  acceptedDate: string;
  calendarYear: string;
  period: string;
  cashAndCashEquivalents: number;
  shortTermInvestments: number;
  cashAndShortTermInvestments: number;
  netReceivables: number;
  inventory: number;
  otherCurrentAssets: number;
  totalCurrentAssets: number;
  propertyPlantEquipmentNet: number;
  goodwill: number;
  intangibleAssets: number;
  goodwillAndIntangibleAssets: number;
  longTermInvestments: number;
  taxAssets: number;
  otherNonCurrentAssets: number;
  totalNonCurrentAssets: number;
  otherAssets: number;
  totalAssets: number;
}

export interface CashFlowData {
  date: string;
  symbol: string;
  reportedCurrency: string;
  cik: string;
  filingDate: string;
  acceptedDate: string;
  fiscalYear: string;
  period: string;
  netIncome: number;
  depreciationAndAmortization: number;
  deferredIncomeTax: number;
  stockBasedCompensation: number;
  changeInWorkingCapital: number;
  accountsReceivables: number;
  inventory: number;
  accountsPayables: number;
  otherWorkingCapital: number;
  otherNonCashItems: number;
  netCashProvidedByOperatingActivities: number;
  investmentsInPropertyPlantAndEquipment: number;
  acquisitionsNet: number;
  purchasesOfInvestments: number;
  salesMaturitiesOfInvestments: number;
  otherInvestingActivities: number;
  netCashProvidedByInvestingActivities: number;
  netDebtIssuance: number;
  longTermNetDebtIssuance: number;
  shortTermNetDebtIssuance: number;
  netStockIssuance: number;
  netCommonStockIssuance: number;
  commonStockIssuance: number;
  commonStockRepurchased: number;
  netPreferredStockIssuance: number;
  netDividendsPaid: number;
  commonDividendsPaid: number;
  preferredDividendsPaid: number;
  otherFinancingActivities: number;
  netCashProvidedByFinancingActivities: number;
  effectOfForexChangesOnCash: number;
  netChangeInCash: number;
  cashAtEndOfPeriod: number;
  cashAtBeginningOfPeriod: number;
  operatingCashFlow: number;
  capitalExpenditure: number;
  freeCashFlow: number;
  incomeTaxesPaid: number;
  interestPaid: number;
}

export interface IncomeStatementData {
  date: string;
  symbol: string;
  reportedCurrency: string;
  cik: string;
  filingDate: string;
  acceptedDate: string;
  fiscalYear: string;
  period: string;
  revenue?: number;
  costOfRevenue?: number;
  grossProfit?: number;
  grossProfitRatio?: number;
  researchAndDevelopmentExpenses?: number;
  generalAndAdministrativeExpenses?: number;
  sellingAndMarketingExpenses?: number;
  sellingGeneralAndAdministrativeExpenses?: number;
  otherExpenses?: number;
  operatingExpenses?: number;
  costAndExpenses?: number;
  interestIncome?: number;
  interestExpense?: number;
  depreciationAndAmortization?: number;
  ebitda?: number;
  ebitdaratio?: number;
  operatingIncome?: number;
  operatingIncomeRatio?: number;
  totalOtherIncomeExpensesNet?: number;
  incomeBeforeTax?: number;
  incomeBeforeTaxRatio?: number;
  incomeTaxExpense?: number;
  netIncome?: number;
  netIncomeRatio?: number;
  eps?: number;
  epsdiluted?: number;
  weightedAverageShsOut?: number;
  weightedAverageShsOutDil?: number;
}

// AlphaVantage API Types
export interface AlphaVantageIncomeStatement {
  fiscalDateEnding: string;
  reportedCurrency: string;
  grossProfit?: string;
  totalRevenue?: string;
  costOfRevenue?: string;
  costofGoodsAndServicesSold?: string;
  operatingIncome?: string;
  sellingGeneralAndAdministrative?: string;
  researchAndDevelopment?: string;
  operatingExpenses?: string;
  investmentIncomeNet?: string;
  netInterestIncome?: string;
  interestIncome?: string;
  interestExpense?: string;
  nonInterestIncome?: string;
  otherNonOperatingIncome?: string;
  depreciation?: string;
  depreciationAndAmortization?: string;
  incomeBeforeTax?: string;
  incomeTaxExpense?: string;
  interestAndDebtExpense?: string;
  netIncomeFromContinuingOperations?: string;
  comprehensiveIncomeNetOfTax?: string;
  ebit?: string;
  ebitda?: string;
  netIncome?: string;
}

export interface AlphaVantageIncomeStatementResponse {
  symbol: string;
  annualReports: AlphaVantageIncomeStatement[];
  quarterlyReports: AlphaVantageIncomeStatement[];
}

export interface AlphaVantageBalanceSheet {
  fiscalDateEnding: string;
  reportedCurrency: string;
  totalAssets?: string;
  totalCurrentAssets?: string;
  cashAndCashEquivalentsAtCarryingValue?: string;
  cashAndShortTermInvestments?: string;
  inventory?: string;
  currentNetReceivables?: string;
  totalNonCurrentAssets?: string;
  propertyPlantEquipment?: string;
  accumulatedDepreciationAmortizationPPE?: string;
  intangibleAssets?: string;
  intangibleAssetsExcludingGoodwill?: string;
  goodwill?: string;
  investments?: string;
  longTermInvestments?: string;
  shortTermInvestments?: string;
  otherCurrentAssets?: string;
  otherNonCurrentAssets?: string;
  totalLiabilities?: string;
  totalCurrentLiabilities?: string;
  currentAccountsPayable?: string;
  deferredRevenue?: string;
  currentDebt?: string;
  shortTermDebt?: string;
  totalNonCurrentLiabilities?: string;
  capitalLeaseObligations?: string;
  longTermDebt?: string;
  currentLongTermDebt?: string;
  longTermDebtNoncurrent?: string;
  shortLongTermDebtTotal?: string;
  otherCurrentLiabilities?: string;
  otherNonCurrentLiabilities?: string;
  totalShareholderEquity?: string;
  treasuryStock?: string;
  retainedEarnings?: string;
  commonStock?: string;
  commonStockSharesOutstanding?: string;
}

export interface AlphaVantageBalanceSheetResponse {
  symbol: string;
  annualReports: AlphaVantageBalanceSheet[];
  quarterlyReports: AlphaVantageBalanceSheet[];
}

export interface AlphaVantageCashFlow {
  fiscalDateEnding: string;
  reportedCurrency: string;
  operatingCashflow?: string;
  paymentsForOperatingActivities?: string;
  proceedsFromOperatingActivities?: string;
  changeInOperatingLiabilities?: string;
  changeInOperatingAssets?: string;
  depreciationDepletionAndAmortization?: string;
  capitalExpenditures?: string;
  changeInReceivables?: string;
  changeInInventory?: string;
  profitLoss?: string;
  cashflowFromInvestment?: string;
  cashflowFromFinancing?: string;
  proceedsFromRepaymentsOfShortTermDebt?: string;
  paymentsForRepurchaseOfCommonStock?: string;
  paymentsForRepurchaseOfEquity?: string;
  paymentsForRepurchaseOfPreferredStock?: string;
  dividendPayout?: string;
  dividendPayoutCommonStock?: string;
  dividendPayoutPreferredStock?: string;
  proceedsFromIssuanceOfCommonStock?: string;
  proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet?: string;
  proceedsFromIssuanceOfPreferredStock?: string;
  proceedsFromRepurchaseOfEquity?: string;
  proceedsFromSaleOfTreasuryStock?: string;
  changeInCashAndCashEquivalents?: string;
  changeInExchangeRate?: string;
  netIncome?: string;
}

export interface AlphaVantageCashFlowResponse {
  symbol: string;
  annualReports: AlphaVantageCashFlow[];
  quarterlyReports: AlphaVantageCashFlow[];
}