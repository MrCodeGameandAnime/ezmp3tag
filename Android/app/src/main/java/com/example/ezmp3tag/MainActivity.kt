package com.example.ezmp3tag

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.OpenableColumns
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import okhttp3.*
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream
import okhttp3.MediaType.Companion.toMediaType
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme
import org.json.JSONObject


class MainActivity : ComponentActivity() {

    private val client = OkHttpClient()
    private var downloadUrl: String? = null // Store the download URL

    // Register a callback for selecting music files
    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val fileName = getFileName(it)
            // Upload the file to the server
            uploadFileToApi(it, fileName)
        } ?: Toast.makeText(this, "No file selected", Toast.LENGTH_SHORT).show()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            EzMP3TagTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    UploadAndAnalyzeUI(
                        onFileSelectClick = {
                            // Launch file picker
                            filePickerLauncher.launch("audio/*")
                        }
                    )
                }
            }
        }
    }

    private fun getFileName(uri: Uri): String {
        var fileName = "unknown"
        val cursor = contentResolver.query(uri, null, null, null, null)
        cursor?.use {
            if (it.moveToFirst()) {
                fileName = it.getString(it.getColumnIndexOrThrow(OpenableColumns.DISPLAY_NAME))
            }
        }
        return fileName
    }

    private fun uploadFileToApi(fileUri: Uri, fileName: String) {
        try {
            val inputStream: InputStream? = contentResolver.openInputStream(fileUri)
            val fileData = inputStream?.readBytes()

            val mediaType = "audio/mpeg".toMediaType()

            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart(
                    "file", fileName,
                    RequestBody.create(mediaType, fileData!!)
                )
                .build()

            // Update the API URL here
            val request = Request.Builder()
                .url("http://192.168.1.214:5000/api/upload") // Use your computer's local IP address
                .post(requestBody)
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    Log.e("MainActivity", "Upload failed: ${e.message}")
                }

                override fun onResponse(call: Call, response: Response) {
                    if (response.isSuccessful) {
                        response.body?.string()?.let { responseBody ->
                            val jsonResponse = JSONObject(responseBody)
                            downloadUrl = jsonResponse.getString("download_url") // Store the download URL
                            Log.i("MainActivity", "Upload successful, ready to download from $downloadUrl")
                            downloadFileFromApi(downloadUrl!!)
                        }
                    } else {
                        Log.e("MainActivity", "Upload failed: ${response.message}")
                    }
                }
            })
        } catch (e: IOException) {
            e.printStackTrace()
            Toast.makeText(this, "Failed to read file", Toast.LENGTH_SHORT).show()
        }
    }

    private fun downloadFileFromApi(downloadUrl: String) {
        val request = Request.Builder()
            .url(downloadUrl) // Use the stored download URL
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("MainActivity", "Download failed: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.byteStream()?.let { inputStream ->
                        saveFileToStorage(inputStream, "downloaded_music.mp3")
                    }
                    Log.i("MainActivity", "Download complete")
                } else {
                    Log.e("MainActivity", "Download failed: ${response.message}")
                }
            }
        })
    }

    private fun saveFileToStorage(inputStream: InputStream, fileName: String) {
        // Ensure you have the WRITE_EXTERNAL_STORAGE permission
        if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 1)
        } else {
            val file = File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), fileName)
            FileOutputStream(file).use { outputStream ->
                inputStream.copyTo(outputStream)
            }
            Log.i("MainActivity", "File saved to ${file.absolutePath}")
        }
    }
}

@Composable
fun UploadAndAnalyzeUI(onFileSelectClick: () -> Unit) {
    var statusMessage by remember { mutableStateOf("Select a music file to upload.") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = statusMessage, style = MaterialTheme.typography.bodyLarge)

        Spacer(modifier = Modifier.height(16.dp))

        Button(onClick = {
            onFileSelectClick()
        }) {
            Text(text = "Upload Music")
        }
    }
}

@Preview(showBackground = true)
@Composable
fun UploadAndAnalyzeUIPreview() {
    EzMP3TagTheme {
        UploadAndAnalyzeUI(onFileSelectClick = {})
    }
}
