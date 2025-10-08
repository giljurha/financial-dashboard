package com.example.financialdashboard.service

import com.example.financialdashboard.model.AlphaVantageBalanceSheetResponse
import com.example.financialdashboard.model.AlphaVantageCashFlowResponse
import com.example.financialdashboard.model.AlphaVantageIncomeStatementResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.springframework.web.reactive.function.client.WebClient
import reactor.core.publisher.Mono

@Service
class AlphaVantageService {

    @Value("\${alphavantage-api.base-url}")
    private lateinit var baseUrl: String

    @Value("\${alphavantage-api.api-key}")
    private lateinit var apiKey: String

    private val webClient = WebClient.builder().build()

    /**
     * Get income statement data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Income statement data
     */
    fun getIncomeStatement(symbol: String): Mono<AlphaVantageIncomeStatementResponse> {
        return webClient.get()
            .uri("$baseUrl?function=INCOME_STATEMENT&symbol=$symbol&apikey=$apiKey")
            .retrieve()
            .bodyToMono(AlphaVantageIncomeStatementResponse::class.java)
    }

    /**
     * Get balance sheet data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Balance sheet data
     */
    fun getBalanceSheet(symbol: String): Mono<AlphaVantageBalanceSheetResponse> {
        return webClient.get()
            .uri("$baseUrl?function=BALANCE_SHEET&symbol=$symbol&apikey=$apiKey")
            .retrieve()
            .bodyToMono(AlphaVantageBalanceSheetResponse::class.java)
    }

    /**
     * Get cash flow statement data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Cash flow statement data
     */
    fun getCashFlowStatement(symbol: String): Mono<AlphaVantageCashFlowResponse> {
        return webClient.get()
            .uri("$baseUrl?function=CASH_FLOW&symbol=$symbol&apikey=$apiKey")
            .retrieve()
            .bodyToMono(AlphaVantageCashFlowResponse::class.java)
    }
}
