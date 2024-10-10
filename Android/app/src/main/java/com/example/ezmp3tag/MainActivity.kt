package com.example.ezmp3tag

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
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
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity() {

    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    // Register file picker callback
    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val fileName = getFileName(it)
            uploadFileToApi(it, fileName)
        } ?: runOnUiThread {
            Toast.makeText(this, "No file selected", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            EzMP3TagTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    UploadUI(onFileSelectClick = {
                        filePickerLauncher.launch("audio/*")
                    })
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
        val networkService = NetworkService(this, client)

        networkService.uploadFile(fileUri, fileName, { downloadUrl ->
            runOnUiThread {
                // Navigate to SuccessActivity
                val intent = Intent(this, SuccessActivity::class.java)
                intent.putExtra("download_url", downloadUrl)
                startActivity(intent)
            }
        }, { errorMessage ->
            runOnUiThread {
                Toast.makeText(this, "Upload failed: $errorMessage", Toast.LENGTH_SHORT).show()
            }
        })
    }
}

@Composable
fun UploadUI(onFileSelectClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(onClick = onFileSelectClick) {
            Text(text = "Upload Music")
        }
    }
}

@Preview(showBackground = true)
@Composable
fun UploadUIPreview() {
    EzMP3TagTheme {
        UploadUI(onFileSelectClick = {})
    }
}



// further separation
/*package com.example.ezmp3tag

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
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
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme
import okhttp3.*
import java.io.InputStream
import java.util.concurrent.TimeUnit
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject
import java.io.IOException

class MainActivity : ComponentActivity() {

    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    // Register file picker callback
    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val fileName = getFileName(it)
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
                    UploadUI(onFileSelectClick = {
                        filePickerLauncher.launch("audio/*")
                    })
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
                .addFormDataPart("file", fileName, RequestBody.create(mediaType, fileData!!))
                .build()

            val request = Request.Builder()
                .url("http://192.168.1.214:5000/api/upload")
                .post(requestBody)
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "Upload failed: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onResponse(call: Call, response: Response) {
                    if (response.isSuccessful) {
                        response.body?.string()?.let { responseBody ->
                            val jsonResponse = JSONObject(responseBody)
                            val downloadUrl = jsonResponse.getString("download_url")

                            // Navigate to SuccessActivity
                            val intent = Intent(this@MainActivity, SuccessActivity::class.java)
                            intent.putExtra("download_url", "http://192.168.1.214:5000$downloadUrl")
                            startActivity(intent)
                        }
                    } else {
                        runOnUiThread {
                            Toast.makeText(this@MainActivity, "Upload failed: ${response.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            })
        } catch (e: IOException) {
            Toast.makeText(this, "Failed to read file", Toast.LENGTH_SHORT).show()
        }
    }
}

@Composable
fun UploadUI(onFileSelectClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(onClick = onFileSelectClick) {
            Text(text = "Upload Music")
        }
    }
}

@Preview(showBackground = true)
@Composable
fun UploadUIPreview() {
    EzMP3TagTheme {
        UploadUI(onFileSelectClick = {})
    }
}*/




// pre modularization
/*
package com.example.ezmp3tag

import android.Manifest
import android.content.Intent
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
import java.util.concurrent.TimeUnit
import okhttp3.MediaType.Companion.toMediaType
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme
import org.json.JSONObject
import androidx.core.content.FileProvider

class MainActivity : ComponentActivity() {

    // Configure OkHttpClient with increased timeout
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    private var downloadUrl: String? = null // Store the download URL
    private var downloadedFilePath: String? = null // Store the path of the downloaded file

    // Register a callback for selecting music files
    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val fileName = getFileName(it)
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
                        },
                        downloadedFilePath = downloadedFilePath,
                        onOpenFileClick = {
                            downloadedFilePath?.let { path -> openFile(path) }
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
                .url("http://192.168.1.214:5000/api/upload") // Use your server IP address
                .post(requestBody)
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    Log.e("MainActivity", "Upload failed: ${e.message}")
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "Upload failed: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onResponse(call: Call, response: Response) {
                    if (response.isSuccessful) {
                        response.body?.string()?.let { responseBody ->
                            val jsonResponse = JSONObject(responseBody)
                            val relativeDownloadUrl = jsonResponse.getString("download_url")
                            // Prepend the server base URL
                            downloadUrl = "http://192.168.1.214:5000$relativeDownloadUrl"
                            Log.i("MainActivity", "Upload successful, ready to download from $downloadUrl")
                            downloadFileFromApi(downloadUrl!!)
                        }
                    } else {
                        Log.e("MainActivity", "Upload failed: ${response.message}")
                        runOnUiThread {
                            Toast.makeText(this@MainActivity, "Upload failed: ${response.message}", Toast.LENGTH_SHORT).show()
                        }
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
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Download failed: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.byteStream()?.let { inputStream ->
                        downloadedFilePath = saveFileToStorage(inputStream, "downloaded_music.mp3")
                    }
                    Log.i("MainActivity", "Download complete")
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "Download complete: $downloadedFilePath", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Log.e("MainActivity", "Download failed: ${response.message}")
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "Download failed: ${response.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun saveFileToStorage(inputStream: InputStream, fileName: String): String {
        if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 1)
            return "" // Return empty string if permission is not granted
        } else {
            val file = File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), fileName)
            FileOutputStream(file).use { outputStream ->
                inputStream.copyTo(outputStream)
            }
            Log.i("MainActivity", "File saved to ${file.absolutePath}")
            return file.absolutePath // Return the file path for later use
        }
    }

    private fun openFile(filePath: String) {
        val file = File(filePath)
        val uri = FileProvider.getUriForFile(this, "${packageName}.provider", file)
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "audio/mpeg")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(intent)
    }
}

@Composable
fun UploadAndAnalyzeUI(onFileSelectClick: () -> Unit, downloadedFilePath: String?, onOpenFileClick: () -> Unit) {
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

        // Show the open file button if a file has been downloaded
        downloadedFilePath?.let {
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = {
                onOpenFileClick()
            }) {
                Text(text = "Open Downloaded Music")
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun UploadAndAnalyzeUIPreview() {
    EzMP3TagTheme {
        UploadAndAnalyzeUI(onFileSelectClick = {}, downloadedFilePath = null, onOpenFileClick = {})

    }
   }

 */