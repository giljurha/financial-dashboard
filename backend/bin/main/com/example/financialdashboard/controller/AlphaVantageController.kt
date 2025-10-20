package com.example.financialdashboard.controller

import com.example.financialdashboard.model.AlphaVantageBalanceSheetResponse
import com.example.financialdashboard.model.AlphaVantageCashFlowResponse
import com.example.financialdashboard.model.AlphaVantageIncomeStatementResponse
import com.example.financialdashboard.service.AlphaVantageService
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import reactor.core.publisher.Mono

@RestController
@RequestMapping("/api/alphavantage")
class AlphaVantageController(private val alphaVantageService: AlphaVantageService) {

    private val logger = LoggerFactory.getLogger(AlphaVantageController::class.java)

    /**
     * Get income statement for a stock symbol
     * Example: GET /api/alphavantage/income-statement/IBM
     */
    @GetMapping("/income-statement/{symbol}")
    fun getIncomeStatement(@PathVariable symbol: String): Mono<ResponseEntity<AlphaVantageIncomeStatementResponse>> {
        return alphaVantageService.getIncomeStatement(symbol)
            .map { ResponseEntity.ok(it) }
            .onErrorResume { error ->
                logger.error("Error in getIncomeStatement endpoint for symbol: $symbol", error)
                Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build())
            }
    }

    /**
     * Get balance sheet for a stock symbol
     * Example: GET /api/alphavantage/balance-sheet/IBM
     */
    @GetMapping("/balance-sheet/{symbol}")
    fun getBalanceSheet(@PathVariable symbol: String): Mono<ResponseEntity<AlphaVantageBalanceSheetResponse>> {
        return alphaVantageService.getBalanceSheet(symbol)
            .map { ResponseEntity.ok(it) }
            .onErrorResume { error ->
                logger.error("Error in getBalanceSheet endpoint for symbol: $symbol", error)
                Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build())
            }
    }

    /**
     * Get cash flow statement for a stock symbol
     * Example: GET /api/alphavantage/cash-flow/IBM
     */
    @GetMapping("/cash-flow/{symbol}")
    fun getCashFlowStatement(@PathVariable symbol: String): Mono<ResponseEntity<AlphaVantageCashFlowResponse>> {
        return alphaVantageService.getCashFlowStatement(symbol)
            .map { ResponseEntity.ok(it) }
            .onErrorResume { error ->
                logger.error("Error in getCashFlowStatement endpoint for symbol: $symbol", error)
                Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build())
            }
    }
}
