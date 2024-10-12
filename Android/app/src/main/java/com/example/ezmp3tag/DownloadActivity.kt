package com.example.ezmp3tag

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme
import okhttp3.OkHttpClient

class DownloadActivity : ComponentActivity() {

    private var downloadUrl: String? = null

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
        val networkService = NetworkService(this, OkHttpClient())

        // Extract the actual filename from the URL
        val fileName = downloadUrl.substring(downloadUrl.lastIndexOf('/') + 1)

        networkService.downloadFile(downloadUrl, fileName, { filePath ->
            // Show success message on the UI thread
            runOnUiThread {
                Toast.makeText(this, "Download complete: $filePath", Toast.LENGTH_LONG).show()
                Log.d("DownloadActivity", "Downloaded file path: $filePath")
            }
        }, { errorMessage ->
            // Show error message on the UI thread
            runOnUiThread {
                Toast.makeText(this, "Download failed: $errorMessage", Toast.LENGTH_SHORT).show()
            }
        })
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
