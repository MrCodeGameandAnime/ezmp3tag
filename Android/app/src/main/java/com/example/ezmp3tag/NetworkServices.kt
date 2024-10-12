package com.example.ezmp3tag

import android.content.Context
import android.net.Uri
import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject
import java.io.IOException
import java.io.InputStream
import java.util.concurrent.TimeUnit

class NetworkService(private val context: Context) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(120, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .build()

    fun uploadFile(fileUri: Uri, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        try {
            val inputStream: InputStream = context.contentResolver.openInputStream(fileUri)
                ?: throw IOException("Failed to open input stream.")

            val mediaType = "audio/mpeg".toMediaType()
            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", fileName, RequestBody.create(mediaType, inputStream.readBytes()))
                .build()

            val request = Request.Builder()
                .url("http://192.168.1.214:5000/api/upload")
                .post(requestBody)
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    Log.e("NetworkService", "Upload failed: ${e.message}")
                    onError("Upload failed: ${e.message}")
                }

                override fun onResponse(call: Call, response: Response) {
                    if (response.isSuccessful) {
                        response.body?.string()?.let {
                            val jsonResponse = JSONObject(it)
                            val downloadUrl = jsonResponse.getString("download_url")
                            Log.d("NetworkService", "Upload successful, download URL: $downloadUrl")
                            onSuccess(downloadUrl)
                        }
                    } else {
                        Log.e("NetworkService", "Upload failed with code: ${response.code}")
                        onError("Upload failed with response code: ${response.code}")
                    }
                }
            })
        } catch (e: IOException) {
            Log.e("NetworkService", "File read failed: ${e.message}")
            onError("File read failed: ${e.message}")
        }
    }

    fun downloadFile(downloadUrl: String, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        val request = Request.Builder()
            .url(downloadUrl)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                // Log error message to Logcat
                Log.e("NetworkService", "Download failed: ${e.message}")
                onError("Download failed: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.byteStream()?.let { inputStream ->
                        try {
                            // Save the file with the provided fileName in the public Downloads directory
                            val filePath = FileUtils.saveFileToStorage(context, inputStream, fileName)
                            Log.d("NetworkService", "Download successful, file path: $filePath")
                            onSuccess(filePath)
                        } catch (e: IOException) {
                            Log.e("NetworkService", "Error saving file: ${e.message}")
                            onError("Error saving file: ${e.message}")
                        }
                    } ?: run {
                        Log.e("NetworkService", "Failed to get input stream")
                        onError("Failed to get input stream.")
                    }
                } else {
                    Log.e("NetworkService", "Download failed with response code: ${response.code}, message: ${response.message}")
                    onError("Download failed with response code: ${response.code}")
                }
            }
        })
    }
}
