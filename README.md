
<h3 align="center">Object Counter</h3>

  <p align="center">
  Object counter in spesific region which using YOLOV8n and OpenCV.
  <br>
  <br>
	In this project our model is customized to only capture the car and bus objects, the image of captured objects are saved in defined paths which seperates object via object type.
	<br>
  <br>
	If object 1 is captured, the track id of object, name of object, region name, saved image path, date/time will send to PostegreSQL database, if object 2 is captured same informations will send to Flask server with SocketIO.
	<br>
  <br>
	<b>PS: Comments and object names written in Turkish</p></b>
 </p align="center">

<!-- ABOUT THE PROJECT -->
<h3 align="center">Built with</h3>
<div align="center" style="color:blue;display:flex;justify-content:center;align-items: center;"; >
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"</img>
<img src="https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white"</img>
</div>
<div align="center" style="color:blue;display:flex;justify-content:center;align-items:center;"; >
<img src="https://img.shields.io/badge/FLASK-79C7D1?style=for-the-badge&logo=flask&logoColor=white"</img>
<img src="https://img.shields.io/badge/Socket.IO-000000?style=for-the-badge&logo=socketdotio&logoColor=white"</img>
</div>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
* <b>Python
  
* PostegreSQL 16 and pgAdmin4</b>
  ```sh
  (requires Homebrew)
  brew install postgresql@16
  brew install --cask pgadmin4
  ```
  
* <b>Flask</b>
  ```sh
  pip install Flask
  ```

* <b>Socket.IO</b>
  ```sh
  npm install socket.io
  ```

* <b>Ultralytics</b>(for model and counter)
  ```sh
  pip install ultralytics
  ```
* <b>OpenCV</b>
  ```sh
  pip install opencv-python
  ```
  


<!-- USAGE EXAMPLES -->
## Usage
* <b>For main application</b>
   ```sh
  python main.py
  ```

* <b>For Flask server</b>
   ```sh
  python app.py
  ```

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
