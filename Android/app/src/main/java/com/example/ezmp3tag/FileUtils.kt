package com.example.ezmp3tag

import android.content.Context
import android.os.Environment
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream

object FileUtils {

    fun saveFileToStorage(context: Context, inputStream: InputStream, fileName: String): String {
        val downloadsDir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)

        if (!downloadsDir?.exists()!! && !downloadsDir.mkdirs()) {
            throw IOException("Unable to create Downloads directory")
        }

        val file = File(downloadsDir, fileName)

        try {
            FileOutputStream(file).use { outputStream ->
                inputStream.copyTo(outputStream)
            }
            Log.d("FileUtils", "File saved: ${file.absolutePath}")
        } catch (e: IOException) {
            Log.e("FileUtils", "Error saving file: ${e.message}")
            throw IOException("Error saving file: ${e.message}")
        }

        return file.absolutePath
    }
}
