package com.example.financialdashboard.controller

import com.example.financialdashboard.model.AlphaVantageBalanceSheetResponse
import com.example.financialdashboard.model.AlphaVantageCashFlowResponse
import com.example.financialdashboard.model.AlphaVantageIncomeStatementResponse
import com.example.financialdashboard.service.AlphaVantageService
import org.springframework.web.bind.annotation.*
import reactor.core.publisher.Mono

@RestController
@RequestMapping("/api/alphavantage")
class AlphaVantageController(private val alphaVantageService: AlphaVantageService) {

    /**
     * Get income statement for a stock symbol
     * Example: GET /api/alphavantage/income-statement/IBM
     */
    @GetMapping("/income-statement/{symbol}")
    fun getIncomeStatement(@PathVariable symbol: String): Mono<AlphaVantageIncomeStatementResponse> {
        return alphaVantageService.getIncomeStatement(symbol)
    }

    /**
     * Get balance sheet for a stock symbol
     * Example: GET /api/alphavantage/balance-sheet/IBM
     */
    @GetMapping("/balance-sheet/{symbol}")
    fun getBalanceSheet(@PathVariable symbol: String): Mono<AlphaVantageBalanceSheetResponse> {
        return alphaVantageService.getBalanceSheet(symbol)
    }

    /**
     * Get cash flow statement for a stock symbol
     * Example: GET /api/alphavantage/cash-flow/IBM
     */
    @GetMapping("/cash-flow/{symbol}")
    fun getCashFlowStatement(@PathVariable symbol: String): Mono<AlphaVantageCashFlowResponse> {
        return alphaVantageService.getCashFlowStatement(symbol)
    }
}
