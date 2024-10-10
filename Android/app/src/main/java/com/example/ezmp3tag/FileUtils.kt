package com.example.ezmp3tag

import android.content.Context
import android.os.Environment
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream

object FileUtils {

    fun saveFileToStorage(context: Context, inputStream: InputStream, fileName: String): String {
        val downloadsDir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
            ?: throw IOException("Unable to access external storage directory")
        val file = File(downloadsDir, fileName)
        FileOutputStream(file).use { outputStream ->
            inputStream.copyTo(outputStream)
        }
        return file.absolutePath
    }
}
