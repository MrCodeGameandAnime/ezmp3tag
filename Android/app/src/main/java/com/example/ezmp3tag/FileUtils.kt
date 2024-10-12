package com.example.ezmp3tag

import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream

object FileUtils {

    fun saveFileToStorage(context: Context, inputStream: InputStream, fileName: String): String {
        // Use the MediaStore API for Android Q and above
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            saveFileToPublicDownloads(context, inputStream, fileName)
        } else {
            saveFileToLegacyDownloads(context, inputStream, fileName)
        }
    }

    // For Android Q and above
    private fun saveFileToPublicDownloads(context: Context, inputStream: InputStream, fileName: String): String {
        // This is available starting from Android 10 (API level 29)
        val resolver = context.contentResolver
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, fileName)
            put(MediaStore.MediaColumns.MIME_TYPE, "audio/mpeg")
            put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
        }

        val uri = resolver.insert(MediaStore.Files.getContentUri("external"), contentValues)

        return if (uri != null) {
            try {
                resolver.openOutputStream(uri)?.use { outputStream ->
                    inputStream.copyTo(outputStream)
                }
                Log.d("FileUtils", "File saved to public downloads: $fileName")
                uri.toString() // Return the URI as string
            } catch (e: IOException) {
                Log.e("FileUtils", "Error saving file: ${e.message}")
                throw IOException("Error saving file: ${e.message}")
            }
        } else {
            throw IOException("Failed to create new media content in public Downloads directory")
        }
    }


    // For Android versions below Q
    private fun saveFileToLegacyDownloads(context: Context, inputStream: InputStream, fileName: String): String {
        val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)

        if (!downloadsDir.exists() && !downloadsDir.mkdirs()) {
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
