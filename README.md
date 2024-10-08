EzMP3Tag
========

EzMP3Tag is Python based AI API with an Android application that allows users to upload MP3 files to a Flask server, analyze and modify their metadata, and download the updated file. The app uses `OkHttp` to communicate with a Flask-based backend and supports secure file sharing using Android's `FileProvider`.

Features
--------

-   **Upload MP3 Files:** Select and upload MP3 files from your Android device to a server for processing.
-   **Analyze Metadata:** The server analyzes and updates metadata, returning a downloadable file.
-   **File Download & Share:** Download the processed file to your device and open it with external apps.
-   **Timeout Handling:** The app manages network timeouts with `OkHttp` for reliable uploads/downloads.
-   **Secure File Sharing:** Uses `FileProvider` for securely sharing files between apps on the device.

Tech Stack
----------

-   **Frontend:**

    -   Android (Kotlin)
    -   Jetpack Compose for UI
    -   OkHttp for networking
    -   FileProvider for secure file sharing
-   **Backend:**

    -   Flask (Python)

Requirements
------------

-   Android Studio with Android SDK
-   A Flask server to handle file uploads and provide metadata services
-   Android 10 or higher

Getting Started
---------------

### Prerequisites

Before running the app, ensure you have the following installed:

-   [Android Studio](https://developer.android.com/studio) for Android development
-   A running Flask server on your local network or hosted remotely, configured to accept MP3 file uploads and return modified files

### Setup Instructions

1.  **Clone the Repository**
```
    git clone https://github.com/your-username/ezmp3tag.git
    cd ezmp3tag
```
2.  **Configure the Flask Server URL**

    In `MainActivity.kt`, update the `uploadFileToApi()` method to point to your Flask server's IP address and port.


```
    val request = Request.Builder()
        .url("http://your-server-ip:5000/api/upload")
        .post(requestBody)
        .build()
```

3.  **Set Up Permissions in `AndroidManifest.xml`**

    Ensure the necessary permissions are included in the `AndroidManifest.xml` file for internet access, file storage, and external file sharing.

4.  **File Provider Configuration**

    Make sure the `FileProvider` is correctly configured in the `AndroidManifest.xml` and a `file_paths.xml` file is added in the `res/xml` folder.


    <provider
        android:name="androidx.core.content.FileProvider"
        android:authorities="${applicationId}.provider"
        android:exported="false"
        android:grantUriPermissions="true">
        <meta-data
            android:name="android.support.FILE_PROVIDER_PATHS"
            android:resource="@xml/file_paths" />
    </provider>


Create the `file_paths.xml` file under `res/xml`:



    <?xml version="1.0" encoding="utf-8"?>
    <paths xmlns:android="http://schemas.android.com/apk/res/android">
        <external-files-path name="downloaded_files" path="." />
    </paths>


5.  **Run the App**

    -   Open the project in Android Studio.
    -   Connect your Android device or use an emulator.
    -   Click "Run" to build and install the app on your device.

Usage
-----

1.  **Uploading an MP3 File:**

    -   Open the app and tap on "Upload Music."
    -   Select an MP3 file from your device.
    -   The file will be uploaded to the server for processing.
2.  **Downloading and Sharing:**

    -   Once the file is processed, the app will notify you that the download is complete.
    -   You can then open the file using any external app capable of playing MP3 files.

Screenshots
-----------

| Upload Screen | Success Screen | Download Screen |
| --- | --- | --- |
| ![Upload Screen](path) | ![Success Screen](path) | ![Download Screen](path) |

Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.