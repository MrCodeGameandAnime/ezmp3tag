package com.example.ezmp3tag

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme

class SuccessActivity : ComponentActivity() {

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
                    SuccessUI(
                        downloadUrl = downloadUrl,
                        onDownloadClick = {
                            // Navigate to DownloadActivity
                            val intent = Intent(this@SuccessActivity, DownloadActivity::class.java)
                            intent.putExtra("download_url", downloadUrl)
                            startActivity(intent)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun SuccessUI(downloadUrl: String?, onDownloadClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("File uploaded successfully!")
        downloadUrl?.let {
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onDownloadClick) {
                Text("Download Music")
            }
        }
    }
}



/*
package com.example.ezmp3tag

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme

class SuccessActivity : ComponentActivity() {

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
                    SuccessUI(
                        downloadUrl = downloadUrl,
                        onDownloadClick = {
                            // Navigate to DownloadActivity
                            val intent = Intent(this@SuccessActivity, DownloadActivity::class.java)
                            intent.putExtra("download_url", downloadUrl)
                            startActivity(intent)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun SuccessUI(downloadUrl: String?, onDownloadClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("File uploaded successfully!")
        downloadUrl?.let {
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onDownloadClick) {
                Text("Download Music")
            }
        }
    }
}
*/
