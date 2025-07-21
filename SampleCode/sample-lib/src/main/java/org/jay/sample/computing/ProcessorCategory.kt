package org.jay.sample.computing

sealed class ProcessorCategory

data object Alpha : ProcessorCategory()

object Beta : ProcessorCategory()

data class Gamma(val extraCapacity: Int) : ProcessorCategory()


