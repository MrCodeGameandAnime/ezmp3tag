package com.example.ezmp3tag

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.OpenableColumns
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.ezmp3tag.ui.theme.EzMP3TagTheme

class MainActivity : ComponentActivity() {

    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val fileName = getFileName(it)
            Log.d("MainActivity", "File selected: $fileName")
            uploadFileToApi(it, fileName)
        } ?: Log.d("MainActivity", "No file selected")
    }

    private val requestPermissionsLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        permissions.entries.forEach { (permission, isGranted) ->
            if (isGranted) {
                Log.d("MainActivity", "$permission granted")
            } else {
                Log.e("MainActivity", "$permission denied")
                Toast.makeText(this, "Permission denied: $permission", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("MainActivity", "Activity created")
        requestPermissions()
        setContent {
            EzMP3TagTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = androidx.compose.material3.MaterialTheme.colorScheme.background
                ) {
                    UploadUI(onFileSelectClick = {
                        if (arePermissionsGranted()) {
                            Log.d("MainActivity", "Permissions granted, launching file picker")
                            filePickerLauncher.launch("audio/*")
                        } else {
                            Log.d("MainActivity", "Permissions not granted")
                        }
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
        Log.d("MainActivity", "Starting upload for file: $fileName")
        val networkService = NetworkService(this)
        networkService.uploadFile(fileUri, fileName, { downloadUrl ->
            Log.d("MainActivity", "Upload complete, received download URL: $downloadUrl")
            val intent = Intent(this, SuccessActivity::class.java)
            intent.putExtra("download_url", downloadUrl)
            startActivity(intent)
        }, { errorMessage ->
            Log.e("MainActivity", "Upload failed: $errorMessage")
            Toast.makeText(this, "Upload failed: $errorMessage", Toast.LENGTH_SHORT).show()
        })
    }

    private fun requestPermissions() {
        val permissions = mutableListOf<String>()

        if (!arePermissionsGranted()) {
            // Request new Android 13+ media permission for audio
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                permissions.add(Manifest.permission.READ_MEDIA_AUDIO)
            } else {
                permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
                if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
                    permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }
            requestPermissionsLauncher.launch(permissions.toTypedArray())
        }
    }


    private fun arePermissionsGranted(): Boolean {
        val readPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            checkSelfPermission(Manifest.permission.READ_MEDIA_AUDIO) == PackageManager.PERMISSION_GRANTED
        } else {
            checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED
        }

        val writePermission = if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED
        } else {
            true // No need for WRITE_EXTERNAL_STORAGE on Android Q and above
        }

        return readPermission && writePermission
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
