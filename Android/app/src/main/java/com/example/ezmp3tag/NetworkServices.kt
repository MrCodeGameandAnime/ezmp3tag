package com.example.ezmp3tag

import android.content.Context
import android.net.Uri
import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.io.InputStream
import java.util.concurrent.TimeUnit

class NetworkService(private val context: Context) {

    // Directly specify the base URL here
    private val baseUrl = "http://192.168.1.214:5000"

    private val client = OkHttpClient.Builder()
        .connectTimeout(120, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .build()

    fun uploadFile(fileUri: Uri, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        var inputStream: InputStream? = null
        try {
            inputStream = context.contentResolver.openInputStream(fileUri)
                ?: throw IOException("Failed to open input stream.")

            val mediaType = context.contentResolver.getType(fileUri)?.toMediaType() ?: "audio/mpeg".toMediaType()
            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", fileName, inputStream.readBytes().toRequestBody(mediaType))
                .build()

            val request = Request.Builder()
                .url("$baseUrl/api/upload") // Use baseUrl directly
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
                            try {
                                val jsonResponse = JSONObject(it)
                                val relativeDownloadUrl = jsonResponse.optString("download_url", "")
                                if (relativeDownloadUrl.isNotEmpty()) {
                                    // Construct the absolute download URL using baseUrl
                                    val downloadUrl = "$baseUrl$relativeDownloadUrl"
                                    Log.d("NetworkService", "Upload successful, download URL: $downloadUrl")
                                    onSuccess(downloadUrl)
                                } else {
                                    Log.e("NetworkService", "Download URL not found in response.")
                                    onError("Download URL not found in response.")
                                }
                            } catch (e: Exception) {
                                Log.e("NetworkService", "JSON parsing error: ${e.message}")
                                onError("JSON parsing error: ${e.message}")
                            }
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
        } finally {
            inputStream?.close() // Ensure stream is closed to avoid memory leaks
        }
    }

    fun downloadFile(downloadUrl: String, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        val request = Request.Builder()
            .url(downloadUrl)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("NetworkService", "Download failed: ${e.message}")
                onError("Download failed: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.byteStream()?.use { inputStream ->
                        try {
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
