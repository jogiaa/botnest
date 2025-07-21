package org.jay.sample.computing

import kotlin.random.Random

class ProcessorDelay(private val delayFactor: Int) {

    fun startProcessing(category: ProcessorCategory): Int {
        return when (category) {
            Alpha -> calculateDelay()
            Beta -> delayFactor
            is Gamma -> calculateDelay(extraInfo = category.extraCapacity)
        }
    }

    private fun calculateDelay(extraInfo: Int = 1): Int {
        return extraInfo * delayFactor * Random.Default.nextInt()
    }
}