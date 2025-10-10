package com.example.financialdashboard.service

import com.example.financialdashboard.model.AlphaVantageBalanceSheetResponse
import com.example.financialdashboard.model.AlphaVantageCashFlowResponse
import com.example.financialdashboard.model.AlphaVantageIncomeStatementResponse
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.web.reactive.function.client.WebClient
import org.springframework.web.reactive.function.client.WebClientResponseException
import reactor.core.publisher.Mono

@Service
class AlphaVantageService {

    private val logger = LoggerFactory.getLogger(AlphaVantageService::class.java)

    @Value("\${alphavantage-api.base-url}")
    private lateinit var baseUrl: String

    @Value("\${alphavantage-api.api-key}")
    private lateinit var apiKey: String

    private val webClient = WebClient.builder()
        .codecs { it.defaultCodecs().maxInMemorySize(16 * 1024 * 1024) }
        .build()

    /**
     * Get income statement data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Income statement data
     */
    fun getIncomeStatement(symbol: String): Mono<AlphaVantageIncomeStatementResponse> {
        val url = "$baseUrl?function=INCOME_STATEMENT&symbol=$symbol&apikey=$apiKey"
        logger.info("Fetching income statement for symbol: $symbol")

        return webClient.get()
            .uri(url)
            .retrieve()
            .onStatus({ status -> status.isError }) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    logger.error("AlphaVantage API error for income statement: status=${response.statusCode()}, body=$body")
                    Mono.error(WebClientResponseException.create(
                        response.statusCode().value(),
                        "AlphaVantage API error",
                        response.headers().asHttpHeaders(),
                        body.toByteArray(),
                        null
                    ))
                }
            }
            .bodyToMono(AlphaVantageIncomeStatementResponse::class.java)
            .doOnError { error ->
                logger.error("Error fetching income statement for $symbol: ${error.message}", error)
            }
            .onErrorResume { error ->
                logger.error("Failed to get income statement for $symbol", error)
                Mono.error(RuntimeException("Failed to fetch income statement from AlphaVantage: ${error.message}", error))
            }
    }

    /**
     * Get balance sheet data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Balance sheet data
     */
    fun getBalanceSheet(symbol: String): Mono<AlphaVantageBalanceSheetResponse> {
        val url = "$baseUrl?function=BALANCE_SHEET&symbol=$symbol&apikey=$apiKey"
        logger.info("Fetching balance sheet for symbol: $symbol")

        return webClient.get()
            .uri(url)
            .retrieve()
            .onStatus({ status -> status.isError }) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    logger.error("AlphaVantage API error for balance sheet: status=${response.statusCode()}, body=$body")
                    Mono.error(WebClientResponseException.create(
                        response.statusCode().value(),
                        "AlphaVantage API error",
                        response.headers().asHttpHeaders(),
                        body.toByteArray(),
                        null
                    ))
                }
            }
            .bodyToMono(AlphaVantageBalanceSheetResponse::class.java)
            .doOnError { error ->
                logger.error("Error fetching balance sheet for $symbol: ${error.message}", error)
            }
            .onErrorResume { error ->
                logger.error("Failed to get balance sheet for $symbol", error)
                Mono.error(RuntimeException("Failed to fetch balance sheet from AlphaVantage: ${error.message}", error))
            }
    }

    /**
     * Get cash flow statement data for a given symbol
     * @param symbol Stock symbol (e.g., "IBM")
     * @return Cash flow statement data
     */
    fun getCashFlowStatement(symbol: String): Mono<AlphaVantageCashFlowResponse> {
        val url = "$baseUrl?function=CASH_FLOW&symbol=$symbol&apikey=$apiKey"
        logger.info("Fetching cash flow statement for symbol: $symbol")

        return webClient.get()
            .uri(url)
            .retrieve()
            .onStatus({ status -> status.isError }) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    logger.error("AlphaVantage API error for cash flow: status=${response.statusCode()}, body=$body")
                    Mono.error(WebClientResponseException.create(
                        response.statusCode().value(),
                        "AlphaVantage API error",
                        response.headers().asHttpHeaders(),
                        body.toByteArray(),
                        null
                    ))
                }
            }
            .bodyToMono(AlphaVantageCashFlowResponse::class.java)
            .doOnError { error ->
                logger.error("Error fetching cash flow for $symbol: ${error.message}", error)
            }
            .onErrorResume { error ->
                logger.error("Failed to get cash flow for $symbol", error)
                Mono.error(RuntimeException("Failed to fetch cash flow from AlphaVantage: ${error.message}", error))
            }
    }
}
