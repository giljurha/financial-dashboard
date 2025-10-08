package com.example.financialdashboard.model

import com.fasterxml.jackson.annotation.JsonProperty
import java.math.BigDecimal

// Income Statement Response from AlphaVantage
data class AlphaVantageIncomeStatementResponse(
    val symbol: String,
    @JsonProperty("annualReports")
    val annualReports: List<AlphaVantageIncomeStatement>,
    @JsonProperty("quarterlyReports")
    val quarterlyReports: List<AlphaVantageIncomeStatement>
)

data class AlphaVantageIncomeStatement(
    @JsonProperty("fiscalDateEnding")
    val fiscalDateEnding: String,
    @JsonProperty("reportedCurrency")
    val reportedCurrency: String,
    @JsonProperty("grossProfit")
    val grossProfit: String?,
    @JsonProperty("totalRevenue")
    val totalRevenue: String?,
    @JsonProperty("costOfRevenue")
    val costOfRevenue: String?,
    @JsonProperty("costofGoodsAndServicesSold")
    val costofGoodsAndServicesSold: String?,
    @JsonProperty("operatingIncome")
    val operatingIncome: String?,
    @JsonProperty("sellingGeneralAndAdministrative")
    val sellingGeneralAndAdministrative: String?,
    @JsonProperty("researchAndDevelopment")
    val researchAndDevelopment: String?,
    @JsonProperty("operatingExpenses")
    val operatingExpenses: String?,
    @JsonProperty("investmentIncomeNet")
    val investmentIncomeNet: String?,
    @JsonProperty("netInterestIncome")
    val netInterestIncome: String?,
    @JsonProperty("interestIncome")
    val interestIncome: String?,
    @JsonProperty("interestExpense")
    val interestExpense: String?,
    @JsonProperty("nonInterestIncome")
    val nonInterestIncome: String?,
    @JsonProperty("otherNonOperatingIncome")
    val otherNonOperatingIncome: String?,
    @JsonProperty("depreciation")
    val depreciation: String?,
    @JsonProperty("depreciationAndAmortization")
    val depreciationAndAmortization: String?,
    @JsonProperty("incomeBeforeTax")
    val incomeBeforeTax: String?,
    @JsonProperty("incomeTaxExpense")
    val incomeTaxExpense: String?,
    @JsonProperty("interestAndDebtExpense")
    val interestAndDebtExpense: String?,
    @JsonProperty("netIncomeFromContinuingOperations")
    val netIncomeFromContinuingOperations: String?,
    @JsonProperty("comprehensiveIncomeNetOfTax")
    val comprehensiveIncomeNetOfTax: String?,
    @JsonProperty("ebit")
    val ebit: String?,
    @JsonProperty("ebitda")
    val ebitda: String?,
    @JsonProperty("netIncome")
    val netIncome: String?
)

// Balance Sheet Response from AlphaVantage
data class AlphaVantageBalanceSheetResponse(
    val symbol: String,
    @JsonProperty("annualReports")
    val annualReports: List<AlphaVantageBalanceSheet>,
    @JsonProperty("quarterlyReports")
    val quarterlyReports: List<AlphaVantageBalanceSheet>
)

data class AlphaVantageBalanceSheet(
    @JsonProperty("fiscalDateEnding")
    val fiscalDateEnding: String,
    @JsonProperty("reportedCurrency")
    val reportedCurrency: String,
    @JsonProperty("totalAssets")
    val totalAssets: String?,
    @JsonProperty("totalCurrentAssets")
    val totalCurrentAssets: String?,
    @JsonProperty("cashAndCashEquivalentsAtCarryingValue")
    val cashAndCashEquivalentsAtCarryingValue: String?,
    @JsonProperty("cashAndShortTermInvestments")
    val cashAndShortTermInvestments: String?,
    @JsonProperty("inventory")
    val inventory: String?,
    @JsonProperty("currentNetReceivables")
    val currentNetReceivables: String?,
    @JsonProperty("totalNonCurrentAssets")
    val totalNonCurrentAssets: String?,
    @JsonProperty("propertyPlantEquipment")
    val propertyPlantEquipment: String?,
    @JsonProperty("accumulatedDepreciationAmortizationPPE")
    val accumulatedDepreciationAmortizationPPE: String?,
    @JsonProperty("intangibleAssets")
    val intangibleAssets: String?,
    @JsonProperty("intangibleAssetsExcludingGoodwill")
    val intangibleAssetsExcludingGoodwill: String?,
    @JsonProperty("goodwill")
    val goodwill: String?,
    @JsonProperty("investments")
    val investments: String?,
    @JsonProperty("longTermInvestments")
    val longTermInvestments: String?,
    @JsonProperty("shortTermInvestments")
    val shortTermInvestments: String?,
    @JsonProperty("otherCurrentAssets")
    val otherCurrentAssets: String?,
    @JsonProperty("otherNonCurrentAssets")
    val otherNonCurrentAssets: String?,
    @JsonProperty("totalLiabilities")
    val totalLiabilities: String?,
    @JsonProperty("totalCurrentLiabilities")
    val totalCurrentLiabilities: String?,
    @JsonProperty("currentAccountsPayable")
    val currentAccountsPayable: String?,
    @JsonProperty("deferredRevenue")
    val deferredRevenue: String?,
    @JsonProperty("currentDebt")
    val currentDebt: String?,
    @JsonProperty("shortTermDebt")
    val shortTermDebt: String?,
    @JsonProperty("totalNonCurrentLiabilities")
    val totalNonCurrentLiabilities: String?,
    @JsonProperty("capitalLeaseObligations")
    val capitalLeaseObligations: String?,
    @JsonProperty("longTermDebt")
    val longTermDebt: String?,
    @JsonProperty("currentLongTermDebt")
    val currentLongTermDebt: String?,
    @JsonProperty("longTermDebtNoncurrent")
    val longTermDebtNoncurrent: String?,
    @JsonProperty("shortLongTermDebtTotal")
    val shortLongTermDebtTotal: String?,
    @JsonProperty("otherCurrentLiabilities")
    val otherCurrentLiabilities: String?,
    @JsonProperty("otherNonCurrentLiabilities")
    val otherNonCurrentLiabilities: String?,
    @JsonProperty("totalShareholderEquity")
    val totalShareholderEquity: String?,
    @JsonProperty("treasuryStock")
    val treasuryStock: String?,
    @JsonProperty("retainedEarnings")
    val retainedEarnings: String?,
    @JsonProperty("commonStock")
    val commonStock: String?,
    @JsonProperty("commonStockSharesOutstanding")
    val commonStockSharesOutstanding: String?
)

// Cash Flow Response from AlphaVantage
data class AlphaVantageCashFlowResponse(
    val symbol: String,
    @JsonProperty("annualReports")
    val annualReports: List<AlphaVantageCashFlow>,
    @JsonProperty("quarterlyReports")
    val quarterlyReports: List<AlphaVantageCashFlow>
)

data class AlphaVantageCashFlow(
    @JsonProperty("fiscalDateEnding")
    val fiscalDateEnding: String,
    @JsonProperty("reportedCurrency")
    val reportedCurrency: String,
    @JsonProperty("operatingCashflow")
    val operatingCashflow: String?,
    @JsonProperty("paymentsForOperatingActivities")
    val paymentsForOperatingActivities: String?,
    @JsonProperty("proceedsFromOperatingActivities")
    val proceedsFromOperatingActivities: String?,
    @JsonProperty("changeInOperatingLiabilities")
    val changeInOperatingLiabilities: String?,
    @JsonProperty("changeInOperatingAssets")
    val changeInOperatingAssets: String?,
    @JsonProperty("depreciationDepletionAndAmortization")
    val depreciationDepletionAndAmortization: String?,
    @JsonProperty("capitalExpenditures")
    val capitalExpenditures: String?,
    @JsonProperty("changeInReceivables")
    val changeInReceivables: String?,
    @JsonProperty("changeInInventory")
    val changeInInventory: String?,
    @JsonProperty("profitLoss")
    val profitLoss: String?,
    @JsonProperty("cashflowFromInvestment")
    val cashflowFromInvestment: String?,
    @JsonProperty("cashflowFromFinancing")
    val cashflowFromFinancing: String?,
    @JsonProperty("proceedsFromRepaymentsOfShortTermDebt")
    val proceedsFromRepaymentsOfShortTermDebt: String?,
    @JsonProperty("paymentsForRepurchaseOfCommonStock")
    val paymentsForRepurchaseOfCommonStock: String?,
    @JsonProperty("paymentsForRepurchaseOfEquity")
    val paymentsForRepurchaseOfEquity: String?,
    @JsonProperty("paymentsForRepurchaseOfPreferredStock")
    val paymentsForRepurchaseOfPreferredStock: String?,
    @JsonProperty("dividendPayout")
    val dividendPayout: String?,
    @JsonProperty("dividendPayoutCommonStock")
    val dividendPayoutCommonStock: String?,
    @JsonProperty("dividendPayoutPreferredStock")
    val dividendPayoutPreferredStock: String?,
    @JsonProperty("proceedsFromIssuanceOfCommonStock")
    val proceedsFromIssuanceOfCommonStock: String?,
    @JsonProperty("proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet")
    val proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet: String?,
    @JsonProperty("proceedsFromIssuanceOfPreferredStock")
    val proceedsFromIssuanceOfPreferredStock: String?,
    @JsonProperty("proceedsFromRepurchaseOfEquity")
    val proceedsFromRepurchaseOfEquity: String?,
    @JsonProperty("proceedsFromSaleOfTreasuryStock")
    val proceedsFromSaleOfTreasuryStock: String?,
    @JsonProperty("changeInCashAndCashEquivalents")
    val changeInCashAndCashEquivalents: String?,
    @JsonProperty("changeInExchangeRate")
    val changeInExchangeRate: String?,
    @JsonProperty("netIncome")
    val netIncome: String?
)
