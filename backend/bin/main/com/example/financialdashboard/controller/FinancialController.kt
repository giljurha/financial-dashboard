package com.example.financialdashboard.controller

import com.example.financialdashboard.model.BalanceSheetResponse
import com.example.financialdashboard.model.CashFlowResponse
import com.example.financialdashboard.model.IncomeStatementResponse
import com.example.financialdashboard.service.FinancialService
import org.springframework.web.bind.annotation.*
import reactor.core.publisher.Flux

@RestController
@RequestMapping("/api/financial")
class FinancialController(private val financialService: FinancialService) {

    @GetMapping("/balance-sheet/{symbol}")
    fun getBalanceSheet(
        @PathVariable symbol: String,
        @RequestParam(defaultValue = "annual") period: String
    ): Flux<BalanceSheetResponse> {
        return financialService.getBalanceSheet(symbol, period)
    }

    @GetMapping("/cash-flow/{symbol}")
    fun getCashFlowStatement(
        @PathVariable symbol: String,
        @RequestParam(defaultValue = "annual") period: String
    ): Flux<CashFlowResponse> {
        return financialService.getCashFlowStatement(symbol, period)
    }

    @GetMapping("/income-statement/{symbol}")
    fun getIncomeStatement(
        @PathVariable symbol: String,
        @RequestParam(defaultValue = "annual") period: String
    ): Flux<IncomeStatementResponse> {
        return financialService.getIncomeStatement(symbol, period)
    }
}