package org.jay.sample.impl

import org.jay.sample.util.Logger

class LowerFileProcessorImpl(logger: Logger) : CapitalizedFileProcessorImpl(logger) {
    override fun doAlterations(originalContent: String): String = originalContent.toLowerCase()
}