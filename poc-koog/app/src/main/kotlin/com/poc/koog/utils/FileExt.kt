package com.poc.koog.utils

import java.io.File

fun File.copyWhileAppendingToName(text: String = "_Modified", extension: String = this.extension): File {
    // This copies the old file and modifies the name to have [text] appended
    // For e.g., "InputFile.kt" -> "InputFile_Modified.kt"
    val newFileName = "$nameWithoutExtension$text.$extension"

    // 3. Create the new File object
    return File(parent, newFileName)
}