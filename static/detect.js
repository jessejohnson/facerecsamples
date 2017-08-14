window.onload = function(){

	//welcome!
	console.log("Detect.js Loaded!");

	var canvas = document.getElementById('canvas');
	var context = canvas.getContext('2d');
	var video = document.getElementById('video');
	//var SOCKET_URL = "ws://echo.websocket.org";
	var SOCKET_URL = "ws://127.0.0.1:5000/get_message"
	var ws = new WebSocket(SOCKET_URL);

	//setup socket
	ws.onopen = function(){
		ws.send("Socket Open!");
	};
	ws.onclose = function(){
		console.log("Socket closed!");
	};
	ws.onmessage = function(event){
		console.log("Got message ", event);
	};
	ws.onerror = function(error){
		console.log("WS Error ", error);
	};

	//add play event listener to the 'video' player
	video.addEventListener('play', function(){
		setInterval(detectAndDraw, 2000);

	});

	if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
		navigator.mediaDevices.getUserMedia({video: true}).then(function(stream){
			console.log("Starting webcam feed...");
			video.src = window.URL.createObjectURL(stream);
			video.play();

		});
	}else{
		console.log("Webcam not available")
	}

	function detectAndDraw(){	
		context.drawImage(video, 0, 0, video.width, video.height);
		ws.send(canvas.toDataURL("image/jpeg"));
	}
}