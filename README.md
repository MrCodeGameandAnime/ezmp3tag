# EzMP3Tag

EzMP3Tag is an Android application that uploads and downloads MP3 files from a backend server. The app allows users to send audio files for processing and retrieve them once they are ready. The project uses OkHttp for network requests and includes file management for saving audio files to the device.



https://github.com/user-attachments/assets/3d3dcd7f-0be6-4c74-8100-b23111bd56f6



## Features
- Upload MP3 files to a server.
- Download processed files from the server.
- Handles timeouts and errors.
- Log activities for easier debugging.
- Supports devices running Android 13 (API Level 33) or higher.

## Prerequisites

To use or develop EzMP3Tag, you'll need the following:
- Android Studio.
- A server will handle the upload and download requests. The base URL for the server is configurable in the code.

## Installation

### 1. Clone the Repository
```
git clone https://github.com/your-username/ezmp3tag.git
cd ezmp3tag
```

### 2. Open the Project in Android Studio

-   Open Android Studio and select **File > Open...**.
-   Navigate to the `EzMP3Tag` directory and open it.

### 3. Update the Base URL

In the `NetworkService.kt` file, set the `baseUrl` to the appropriate server URL for file uploads and downloads. The default is set to `http://192.168.1.214:5000`, but you may need to change it based on your setup.



`private val baseUrl = "http://your-server-ip:5000" // Replace with your server URL`

### 4\. Build and Run the Project

-   Connect an Android device or start an emulator.
-   Click the **Run** button in Android Studio to build and install the app on your device.

Usage
-----

### Uploading Files

1.  Select an MP3 file to upload.
2.  The app will send the file to the backend server at `{BASE_URL}/api/upload`.
3.  A toast/log message will notify the user of success or failure.

### Downloading Files

1.  Once the server processes the file, the download URL is returned.
2.  The app will attempt to download the processed file and save it in the device's Downloads folder.
3.  Logs will indicate the status of the download.

Project Structure
-----------------

-   **NetworkService.kt**: Handles network operations like file uploads and downloads.
-   **FileUtils.kt**: Utility class for saving files to storage.
-   **MainActivity.kt**: The main entry point of the app, handling user interaction.
-   **SuccessActivity.kt**: Displays success messages or handles after-upload actions.
-   **DownloadActivity.kt**: Handles downloading and saving files.

Requirements
------------

-   Minimum Android SDK: 33 (Android 13)
-   OkHttp for network requests
-   File I/O for saving and retrieving files

License
-------

EzMP3Tag is licensed under the MIT License. See `LICENSE` for more information.

Contributing
------------

If you'd like to contribute, feel free to fork the repository and submit a pull request. Contributions are welcome!

1.  Fork the repository
2.  Create a new branch (`git checkout -b feature-branch`)
3.  Make your changes
4.  Push to the branch (`git push origin feature-branch`)
5.  Submit a pull request

Contact
-------

For questions or support, please get in touch with the maintainer:

-   Email: mrcodegameandanime@gmail.com
-   GitHub: [MrCodeGameAndAnime](https://github.com/MrCodeGameandAnime)



 ### Key Points Covered:
- **Features**: Overview of what the app does.
- **Installation**: Step-by-step guide to get the app running.
- **Usage**: How to upload and download files using the app.
- **Project Structure**: Describes the key components of the app.
- **License** and **Contributing** sections.
