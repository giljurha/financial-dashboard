package com.example.financialdashboard.model

import com.fasterxml.jackson.annotation.JsonProperty
import java.math.BigDecimal

data class BalanceSheetResponse(
    val symbol: String,
    val date: String,
    @JsonProperty("reportedCurrency")
    val reportedCurrency: String,
    @JsonProperty("cik")
    val cik: String,
    @JsonProperty("fillingDate")
    val fillingDate: String,
    @JsonProperty("acceptedDate")
    val acceptedDate: String,
    @JsonProperty("calendarYear")
    val calendarYear: String,
    @JsonProperty("period")
    val period: String,
    @JsonProperty("cashAndCashEquivalents")
    val cashAndCashEquivalents: BigDecimal,
    @JsonProperty("shortTermInvestments")
    val shortTermInvestments: BigDecimal,
    @JsonProperty("cashAndShortTermInvestments")
    val cashAndShortTermInvestments: BigDecimal,
    @JsonProperty("netReceivables")
    val netReceivables: BigDecimal,
    @JsonProperty("inventory")
    val inventory: BigDecimal,
    @JsonProperty("otherCurrentAssets")
    val otherCurrentAssets: BigDecimal,
    @JsonProperty("totalCurrentAssets")
    val totalCurrentAssets: BigDecimal,
    @JsonProperty("propertyPlantEquipmentNet")
    val propertyPlantEquipmentNet: BigDecimal,
    @JsonProperty("goodwill")
    val goodwill: BigDecimal,
    @JsonProperty("intangibleAssets")
    val intangibleAssets: BigDecimal,
    @JsonProperty("goodwillAndIntangibleAssets")
    val goodwillAndIntangibleAssets: BigDecimal,
    @JsonProperty("longTermInvestments")
    val longTermInvestments: BigDecimal,
    @JsonProperty("taxAssets")
    val taxAssets: BigDecimal,
    @JsonProperty("otherNonCurrentAssets")
    val otherNonCurrentAssets: BigDecimal,
    @JsonProperty("totalNonCurrentAssets")
    val totalNonCurrentAssets: BigDecimal,
    @JsonProperty("otherAssets")
    val otherAssets: BigDecimal,
    @JsonProperty("totalAssets")
    val totalAssets: BigDecimal
)

data class CashFlowResponse(
    val date: String,
    val symbol: String,
    @JsonProperty("reportedCurrency")
    val reportedCurrency: String,
    val cik: String,
    @JsonProperty("filingDate")
    val filingDate: String,
    @JsonProperty("acceptedDate")
    val acceptedDate: String,
    @JsonProperty("fiscalYear")
    val fiscalYear: String,
    val period: String,
    @JsonProperty("netIncome")
    val netIncome: BigDecimal,
    @JsonProperty("depreciationAndAmortization")
    val depreciationAndAmortization: BigDecimal,
    @JsonProperty("deferredIncomeTax")
    val deferredIncomeTax: BigDecimal,
    @JsonProperty("stockBasedCompensation")
    val stockBasedCompensation: BigDecimal,
    @JsonProperty("changeInWorkingCapital")
    val changeInWorkingCapital: BigDecimal,
    @JsonProperty("accountsReceivables")
    val accountsReceivables: BigDecimal,
    val inventory: BigDecimal,
    @JsonProperty("accountsPayables")
    val accountsPayables: BigDecimal,
    @JsonProperty("otherWorkingCapital")
    val otherWorkingCapital: BigDecimal,
    @JsonProperty("otherNonCashItems")
    val otherNonCashItems: BigDecimal,
    @JsonProperty("netCashProvidedByOperatingActivities")
    val netCashProvidedByOperatingActivities: BigDecimal,
    @JsonProperty("investmentsInPropertyPlantAndEquipment")
    val investmentsInPropertyPlantAndEquipment: BigDecimal,
    @JsonProperty("acquisitionsNet")
    val acquisitionsNet: BigDecimal,
    @JsonProperty("purchasesOfInvestments")
    val purchasesOfInvestments: BigDecimal,
    @JsonProperty("salesMaturitiesOfInvestments")
    val salesMaturitiesOfInvestments: BigDecimal,
    @JsonProperty("otherInvestingActivities")
    val otherInvestingActivities: BigDecimal,
    @JsonProperty("netCashProvidedByInvestingActivities")
    val netCashProvidedByInvestingActivities: BigDecimal,
    @JsonProperty("netDebtIssuance")
    val netDebtIssuance: BigDecimal,
    @JsonProperty("longTermNetDebtIssuance")
    val longTermNetDebtIssuance: BigDecimal,
    @JsonProperty("shortTermNetDebtIssuance")
    val shortTermNetDebtIssuance: BigDecimal,
    @JsonProperty("netStockIssuance")
    val netStockIssuance: BigDecimal,
    @JsonProperty("netCommonStockIssuance")
    val netCommonStockIssuance: BigDecimal,
    @JsonProperty("commonStockIssuance")
    val commonStockIssuance: BigDecimal,
    @JsonProperty("commonStockRepurchased")
    val commonStockRepurchased: BigDecimal,
    @JsonProperty("netPreferredStockIssuance")
    val netPreferredStockIssuance: BigDecimal,
    @JsonProperty("netDividendsPaid")
    val netDividendsPaid: BigDecimal,
    @JsonProperty("commonDividendsPaid")
    val commonDividendsPaid: BigDecimal,
    @JsonProperty("preferredDividendsPaid")
    val preferredDividendsPaid: BigDecimal,
    @JsonProperty("otherFinancingActivities")
    val otherFinancingActivities: BigDecimal,
    @JsonProperty("netCashProvidedByFinancingActivities")
    val netCashProvidedByFinancingActivities: BigDecimal,
    @JsonProperty("effectOfForexChangesOnCash")
    val effectOfForexChangesOnCash: BigDecimal,
    @JsonProperty("netChangeInCash")
    val netChangeInCash: BigDecimal,
    @JsonProperty("cashAtEndOfPeriod")
    val cashAtEndOfPeriod: BigDecimal,
    @JsonProperty("cashAtBeginningOfPeriod")
    val cashAtBeginningOfPeriod: BigDecimal,
    @JsonProperty("operatingCashFlow")
    val operatingCashFlow: BigDecimal,
    @JsonProperty("capitalExpenditure")
    val capitalExpenditure: BigDecimal,
    @JsonProperty("freeCashFlow")
    val freeCashFlow: BigDecimal,
    @JsonProperty("incomeTaxesPaid")
    val incomeTaxesPaid: BigDecimal,
    @JsonProperty("interestPaid")
    val interestPaid: BigDecimal
)

data class IncomeStatementResponse(
    val date: String,
    val symbol: String,
    @JsonProperty("reportedCurrency")
    val reportedCurrency: String,
    val cik: String,
    @JsonProperty("filingDate")
    val filingDate: String,
    @JsonProperty("acceptedDate")
    val acceptedDate: String,
    @JsonProperty("fiscalYear")
    val fiscalYear: String,
    val period: String,
    @JsonProperty("revenue")
    val revenue: BigDecimal?,
    @JsonProperty("costOfRevenue")
    val costOfRevenue: BigDecimal?,
    @JsonProperty("grossProfit")
    val grossProfit: BigDecimal?,
    @JsonProperty("grossProfitRatio")
    val grossProfitRatio: BigDecimal?,
    @JsonProperty("researchAndDevelopmentExpenses")
    val researchAndDevelopmentExpenses: BigDecimal?,
    @JsonProperty("generalAndAdministrativeExpenses")
    val generalAndAdministrativeExpenses: BigDecimal?,
    @JsonProperty("sellingAndMarketingExpenses")
    val sellingAndMarketingExpenses: BigDecimal?,
    @JsonProperty("sellingGeneralAndAdministrativeExpenses")
    val sellingGeneralAndAdministrativeExpenses: BigDecimal?,
    @JsonProperty("otherExpenses")
    val otherExpenses: BigDecimal?,
    @JsonProperty("operatingExpenses")
    val operatingExpenses: BigDecimal?,
    @JsonProperty("costAndExpenses")
    val costAndExpenses: BigDecimal?,
    @JsonProperty("interestIncome")
    val interestIncome: BigDecimal?,
    @JsonProperty("interestExpense")
    val interestExpense: BigDecimal?,
    @JsonProperty("depreciationAndAmortization")
    val depreciationAndAmortization: BigDecimal?,
    @JsonProperty("ebitda")
    val ebitda: BigDecimal?,
    @JsonProperty("ebitdaratio")
    val ebitdaratio: BigDecimal?,
    @JsonProperty("operatingIncome")
    val operatingIncome: BigDecimal?,
    @JsonProperty("operatingIncomeRatio")
    val operatingIncomeRatio: BigDecimal?,
    @JsonProperty("totalOtherIncomeExpensesNet")
    val totalOtherIncomeExpensesNet: BigDecimal?,
    @JsonProperty("incomeBeforeTax")
    val incomeBeforeTax: BigDecimal?,
    @JsonProperty("incomeBeforeTaxRatio")
    val incomeBeforeTaxRatio: BigDecimal?,
    @JsonProperty("incomeTaxExpense")
    val incomeTaxExpense: BigDecimal?,
    @JsonProperty("netIncome")
    val netIncome: BigDecimal?,
    @JsonProperty("netIncomeRatio")
    val netIncomeRatio: BigDecimal?,
    @JsonProperty("eps")
    val eps: BigDecimal?,
    @JsonProperty("epsdiluted")
    val epsdiluted: BigDecimal?,
    @JsonProperty("weightedAverageShsOut")
    val weightedAverageShsOut: BigDecimal?,
    @JsonProperty("weightedAverageShsOutDil")
    val weightedAverageShsOutDil: BigDecimal?
)