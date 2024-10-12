package com.example.ezmp3tag

import android.content.Context
import android.os.Environment
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream

object FileUtils {

    fun saveFileToStorage(context: Context, inputStream: InputStream, fileName: String): String {
        // Use the public Downloads directory
        val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)

        // Create the Downloads directory if it doesn't exist
        if (!downloadsDir.exists() && !downloadsDir.mkdirs()) {
            throw IOException("Unable to create Downloads directory")
        }

        // Create the file in the Downloads directory
        val file = File(downloadsDir, fileName)

        // Use FileOutputStream to write the input stream to the file
        try {
            FileOutputStream(file).use { outputStream ->
                inputStream.copyTo(outputStream)
            }
        } catch (e: IOException) {
            throw IOException("Error saving file: ${e.message}")
        }

        // Return the absolute path of the saved file
        return file.absolutePath
    }
}
