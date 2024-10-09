package com.example.ezmp3tag

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Environment
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme
import okhttp3.*
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream

class DownloadActivity : ComponentActivity() {

    private val client = OkHttpClient()
    private var downloadUrl: String? = null
    private var downloadedFilePath: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        downloadUrl = intent.getStringExtra("download_url")

        setContent {
            EzMP3TagTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    DownloadUI(
                        onDownloadClick = { downloadUrl?.let { downloadFileFromApi(it) } }
                    )
                }
            }
        }
    }

    private fun downloadFileFromApi(downloadUrl: String) {
        val request = Request.Builder()
            .url(downloadUrl)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@DownloadActivity, "Download failed: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.byteStream()?.let { inputStream ->
                        downloadedFilePath = saveFileToStorage(inputStream, "downloaded_music.mp3")
                    }
                    runOnUiThread {
                        Toast.makeText(this@DownloadActivity, "Download complete", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    runOnUiThread {
                        Toast.makeText(this@DownloadActivity, "Download failed: ${response.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun saveFileToStorage(inputStream: InputStream, fileName: String): String {
        if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 1)
            return ""
        } else {
            val file = File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), fileName)
            FileOutputStream(file).use { outputStream ->
                inputStream.copyTo(outputStream)
            }
            return file.absolutePath
        }
    }
}

@Composable
fun DownloadUI(onDownloadClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Ready to download your music file!")

        Spacer(modifier = Modifier.height(16.dp))

        Button(onClick = onDownloadClick) {
            Text("Download File")
        }
    }
}

@Preview(showBackground = true)
@Composable
fun DownloadUIPreview() {
    EzMP3TagTheme {
        DownloadUI(onDownloadClick = {})
    }
}
