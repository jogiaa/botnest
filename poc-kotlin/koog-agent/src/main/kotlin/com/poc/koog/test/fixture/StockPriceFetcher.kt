package com.poc.koog.test.fixture

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

data class StockQuote(
    val symbol: String,
    val price: Double
)

interface StockPriceFetcher {
    fun fetchStockPrice(ticker: String): StockQuote
}

class DefaultStockPriceFetcher(
    private val apiKey: String
): StockPriceFetcher {

    override fun fetchStockPrice(ticker: String): StockQuote {
        val urlString = "https://financialmodelingprep.com/api/v3/quote-short/$ticker?apikey=$apiKey"
        var connection: HttpURLConnection? = null

        try {
            val url = URL(urlString)
            connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            val responseCode = connection.responseCode
            if (responseCode != HttpURLConnection.HTTP_OK) {
                // You might want to read the error stream here for more details
                throw IOException("HTTP error code: $responseCode")
            }

            val body = connection.inputStream.bufferedReader().use { it.readText() }

            return parseStockQuote(body, ticker)

        } catch (e: IOException) {
            println("Error fetching stock data: ${e.message}")
            throw e
        } finally {
            connection?.disconnect()
        }
    }

    private fun parseStockQuote(jsonBody: String, ticker: String): StockQuote {
        val priceRegex = "\"price\"\\s*:\\s*([0-9.]+)".toRegex()
        val matchResult = priceRegex.find(jsonBody)
        val price = matchResult?.groups?.get(1)?.value?.toDoubleOrNull()

        return if (price != null) {
            StockQuote(ticker, price)
        } else {
            throw NullPointerException("Could not parse stock price for $ticker in $jsonBody")
        }
    }
}