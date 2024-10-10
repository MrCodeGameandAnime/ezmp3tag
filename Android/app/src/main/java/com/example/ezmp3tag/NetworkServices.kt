package com.example.ezmp3tag

import android.content.Context
import android.net.Uri
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.InputStream

class NetworkService(private val context: Context, private val client: OkHttpClient) {

    fun uploadFile(fileUri: Uri, fileName: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        try {
            val inputStream: InputStream? = context.contentResolver.openInputStream(fileUri)
            val fileData = inputStream?.readBytes() ?: throw IOException("File input stream is null")
            val mediaType = "audio/mpeg".toMediaType()

            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", fileName, RequestBody.create(mediaType, fileData))
                .build()

            val request = Request.Builder()
                .url("http://192.168.1.214:5000/api/upload")
                .post(requestBody)
                .build()

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

    fun downloadFile(downloadUrl: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
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
                        val filePath = FileUtils.saveFileToStorage(context, inputStream, "downloaded_music.mp3")
                        onSuccess(filePath)
                    } ?: onError("Failed to get input stream")
                } else {
                    onError("Download failed: ${response.message}")
                }
            }
        })
    }
}
