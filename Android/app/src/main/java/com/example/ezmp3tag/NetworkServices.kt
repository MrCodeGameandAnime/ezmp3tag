package com.example.ezmp3tag

import android.content.Context
import android.net.Uri
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject
import java.io.IOException
import java.io.InputStream

class NetworkService(private val context: Context, private val client: OkHttpClient) {

    fun uploadFile(fileUri: Uri, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        try {
            // Use ContentResolver to get the input stream
            val inputStream: InputStream = context.contentResolver.openInputStream(fileUri)
                ?: throw IOException("Failed to open input stream.")

            // Create a request body with the file data
            val mediaType = "audio/mpeg".toMediaType()
            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", fileName, RequestBody.create(mediaType, inputStream.readBytes()))
                .build()

            // Create a request
            val request = Request.Builder()
                .url("http://192.168.1.214:5000/api/upload")
                .post(requestBody)
                .build()

            // Execute the request
            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    onError("Upload failed: ${e.message}")
                }

                override fun onResponse(call: Call, response: Response) {
                    if (response.isSuccessful) {
                        response.body?.string()?.let { responseBody ->
                            val jsonResponse = JSONObject(responseBody)
                            val downloadUrl = jsonResponse.getString("download_url")
                            onSuccess("http://192.168.1.214:5000$downloadUrl")
                        } ?: onError("Response body is null")
                    } else {
                        onError("Upload failed: ${response.message}")
                    }
                }
            })
        } catch (e: IOException) {
            onError("Failed to read file: ${e.message}")
        }
    }


    fun downloadFile(downloadUrl: String, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        val request = Request.Builder()
            .url(downloadUrl)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                onError("Download failed: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.byteStream()?.let { inputStream ->
                        // Save the file with the provided fileName using FileUtils
                        try {
                            val filePath = FileUtils.saveFileToStorage(context, inputStream, fileName)
                            onSuccess(filePath)
                        } catch (e: IOException) {
                            onError("Error saving file: ${e.message}")
                        }
                    } ?: onError("Failed to get input stream")
                } else {
                    onError("Download failed: ${response.message}")
                }
            }
        })
    }
}
