$(document).ready(function() {

    // ---------------- Global Variables---------------------
    // ------------------------------------------------------
    
    var API_BASE_URL = ""

    var STANDARD_FILE_NAME = "";
    var STANDARD_FILE_EXTENSION = "";

    var GRABCUT_FILE_NAME = "";
    var GRABCUT_FILE_EXTENSION = "";
    var GRABCUT_COUNT = 1;
    var ACTIVE_GRABCUT_SESSION = false;
    var ACTIVE_GRABCUT_BOUNDING_BOX = [-1, -1, -1, -1];
    var ACTIVE_GRABCUT_SESSION_KEY = "-1";
    var ACTIVE_GRABCUT_SESSION_MODE = "basic";

    

    var isDrawing = false;
    var CANVAS_MODE = "box"
    var NUMBER_CANVAS_BOUNDINGBOX_CLICKS = 0;
    var BOUNDINGBOX_SET = false;
    var ACTIVE_BOUNDINGBOX_CLICK_COORDINATES = [[0, 0], [0, 0], [0, 0], [0, 0]];
    
    var canvas = document.getElementById('GrabcutModificationCanvas');
    var canvasContext = canvas.getContext('2d');
    canvasContext.fillStyle = 'white';
    canvasContext.lineWidth = 0.5;
    var canvasActive = false;

    var BATCHES = {
        count: 0,
        records: []
    };

    // -------------- End Global Variables-------------------
    // ------------------------------------------------------

    // ------------- General AJAX Handlers ------------------
    // ------------------------------------------------------

    /**
     * A generic AJAX handler for all outgoing POST requests
     * @param {String} pathUrl The url to send the request to
     * @param {String} bodyData The stringified JSON request body
     * @param {Function} successCallback The callback function to call on a successful response
     */
    function SendPostAJAXRequest(pathUrl, bodyData, successCallback) {
        $.ajax({
            type: 'post',
            url: pathUrl,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            data: bodyData,
            success: successCallback
        });
    }

    /**
     * A generic AJAX handler for all outgoing GET requests
     * @param {String} pathUrl The url to send the request to
     * @param {Function} successCallback The callback function to call on a successful response
     */
    function SendGetAJAXRequest(pathUrl, successCallback) {
        $.ajax({
            type: 'get',
            url: pathUrl,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            success: successCallback
        });
    }

    /**
     * A generic AJAX handler for all outgoing POST requests with image attachments
     * @param {String} pathUrl The url to send the request to
     * @param {String} bodyData The FormData for the request
     * @param {Function} successCallback The callback function to call on a successful response
     */
    function SendPostAJAXRequestWithImage(pathUrl, bodyData, successCallback) {
        $.ajax({
            url: pathUrl,
            type: 'post',
            data: bodyData,
            cache: false,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: successCallback
        });
    }

    // ----------- End General AJAX Handlers ----------------
    // ------------------------------------------------------

    // --------- Business Logic HTTP Requests ---------------
    // ------------------------------------------------------

    function SendImageForStandardProcessing(image, format, inferenceMode) {
        var url = API_BASE_URL + "/standard";
        var successCallback = SendImageForStandardProcessingResponseHandler;

        // Embed the image via FormData
        var fd = new FormData();
        if (fd) {
            fd.append('id', 0);
            fd.append('subId', 0);
            fd.append('image', image);
            fd.append('imageFormat', format);
            fd.append('inferenceMode', inferenceMode);
        }

        // Execute the HTTP Call
        SendPostAJAXRequestWithImage(url, fd, successCallback);
    }

    function SendImageForGrabcutProcessing(image, format, overlay, overlayFormat, imageWidth, imageHeight, boundingBox, grabcutMode, currentCount, sessionKey) {
        var url = API_BASE_URL + "/grabcut";
        var successCallback = SendImageForGrabcutProcessingResponseHandler;

        // Embed the image via FormData
        var fd = new FormData();
        if (fd) {
            fd.append('id', 0);
            fd.append('subId', 0);
            fd.append('image', image);
            fd.append('imageFormat', format);
            fd.append('adjustmentMap', overlay);
            fd.append('adjustmentMapFormat', overlayFormat);
            fd.append('imageWidth', imageWidth);
            fd.append('imageHeight', imageHeight);
            fd.append('boundingBox', boundingBox);
            fd.append('grabcutMode', grabcutMode);
            fd.append('iterationCount', currentCount);
            fd.append('sessionKey', sessionKey);
        }

        // Execute the HTTP Call
        SendPostAJAXRequestWithImage(url, fd, successCallback);
    }

    function SendImageForStandardBatchProcessing(image, format, id, subId, inferenceMode) {
        var url = API_BASE_URL + "/standard";
        var successCallback = SendImageForStandardBatchProcessingResponseHandler;

        // Embed the image via FormData
        var fd = new FormData();
        if (fd) {
            fd.append('id', id);
            fd.append('subId', subId);
            fd.append('image', image);
            fd.append('imageFormat', format);
            fd.append('inferenceMode',inferenceMode);
        }

        // Execute the HTTP Call
        SendPostAJAXRequestWithImage(url, fd, successCallback);
    }

    function ClearGrabcutSession() {
        var url = API_BASE_URL + "/clear-grabcut-session";
        var successCallback = ClearGrabcutSessionResponseHandler;

        var fd = new FormData();
        if (fd) {
            fd.append('sessionKey', ACTIVE_GRABCUT_SESSION_KEY)
        }

        // Execute the HTTP Call
        SendPostAJAXRequestWithImage(url, fd, successCallback);
    }

    // --------- End Business Logic HTTP Requests -----------
    // ------------------------------------------------------

    // ----------- Callback Handler Functions ---------------
    // ------------------------------------------------------

    function SendImageForStandardProcessingResponseHandler(responseText) {
        var ProcessedImage = responseText.processedImage;
        var ImageFormat = responseText.imageFormat;
        var standardImageOutput_processed = document.getElementById('StandardImageOutput_processed');
        standardImageOutput_processed.src = ProcessedImage;
        $("#StandardImageOutput_processed").show();
        $("#StandardProcessedImageDescription").show();
        $("#SaveStandardProcessedImageButton").show();
        $("#ClearStandardButtonDescription").show();
        $("#ClearStandardButton").show();
    }

    function SendImageForGrabcutProcessingResponseHandler(responseText) {

        GRABCUT_COUNT += 1;

        var ProcessedImage = responseText.processedImage;
        ACTIVE_GRABCUT_SESSION_KEY = responseText.sessionKey;

        var ImageFormat = responseText.imageFormat;
        var standardImageOutput_processed = document.getElementById('GrabcutImageOutput_processed');
        standardImageOutput_processed.src = ProcessedImage;
        // standardImageOutput_processed.src = "data:image/" + ImageFormat + ";base64," + ProcessedImage;
        $("#GrabcutImageOutput_processed").show();
        $("#GrabcutProcessedImageDescription").show();
        $("#SaveGrabcutProcessedImageButton").show();

    }

    function SendImageForStandardBatchProcessingResponseHandler(responseText) {
        let batchId = responseText.id;
        let batchSubId = responseText.subId;
        let ProcessedImage = responseText.processedImage;

        let curBatch = BATCHES.records.find(x => x.id == batchId);
        let curImage = curBatch.images.find(x => x.subId == batchSubId);

        curImage.src = ProcessedImage;
        curBatch.currentProcessedCount += 1;

        if (curBatch.currentProcessedCount == curBatch.totalCount) {
            // We now have processed all images in the batch
            // need to go through and bundle all the images into a zip file and remove the batch from BATCHES
            bundleZipFile(BATCHES.records.find(x => x.id == batchId));
        }

    }

    function ClearGrabcutSessionResponseHandler(responseText) {
        let status = responseText.status;

        if (status === "success") {

            // Reset session variables
            GRABCUT_FILE_NAME = "";
            GRABCUT_FILE_EXTENSION = "";
            GRABCUT_COUNT = 1;
            ACTIVE_GRABCUT_SESSION = false;
            ACTIVE_GRABCUT_BOUNDING_BOX = [-1, -1, -1, -1];
            ACTIVE_GRABCUT_SESSION_KEY = "-1";
            ACTIVE_GRABCUT_SESSION_MODE = "basic";
            CANVAS_MODE = "box";
            NUMBER_CANVAS_BOUNDINGBOX_CLICKS = 0;
            BOUNDINGBOX_SET = false;
            ACTIVE_BOUNDINGBOX_CLICK_COORDINATES = [[0, 0], [0, 0], [0, 0], [0, 0]];

            // Hide initial content
            $("#GrabcutModeSelectDescription").hide("fast");
            document.getElementById('GrabcutModeSelect').disabled = false;
            document.getElementById('GrabcutModeSelect').value = "0";
            $("#GrabcutModeSelect").hide("fast");
            $("#GrabcutInstructions").hide("fast");
            $("#GrabcutOptionSelect").hide("fast");
            $("#ClearInstructions").hide("fast");
            $("#ClearGrabcutCanvasButton").hide("fast");
            $("#GrabcutProcessImageDescription").hide("fast");
            $("#GrabcutImageUploadButton").hide("fast");
            $("#ClearGrabcutButtonDescription").hide("fast");
            $("#ClearGrabcutButton").hide("fast");

            // Clear the canvas, initial image file, all img srcs
            var canvasBackgroundImage = document.getElementById('CanvasBackgroundImage');
            canvasBackgroundImage.src = "";
            $("#CanvasBackgroundImage").hide("fast");

            canvasContext.clearRect(0,0, canvas.width, canvas.height);
            document.getElementById("GrabcutImageUploadFile").value = "";

            var standardImageOutput_processed = document.getElementById('GrabcutImageOutput_processed');
            standardImageOutput_processed.src = "";
            $("#GrabcutImageOutput_processed").hide("fast");
            $("#GrabcutProcessedImageDescription").hide("fast");
            $("#SaveGrabcutProcessedImageButton").hide("fast");

        } else {
            // Uh Oh
        }
    }

    // --------- End Callback Handler Functions -------------
    // ------------------------------------------------------

    // ---------------- Element Handlers --------------------
    // ------------------------------------------------------

    $("#StandardImageUploadFile").change(function() {
        // Check to ensure that the file API is supported in the user's browser
        if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
            //alert('The File APIs are not fully supported in this browser.');
            document.getElementById("AlertMessageBoxText").innerHTML = "The File APIs are not fully supported in this browser.";
            $("#AlertMessageBox").dialog("open");
            return;
        }

        var input = document.getElementById("StandardImageUploadFile");
        if (!input) {
            //alert("File could not be found");
            document.getElementById("AlertMessageBoxText").innerHTML = "File could not be found";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files) {
            //alert("This browser doesn't seem to support the `files` property of file inputs.");
            document.getElementById("AlertMessageBoxText").innerHTML = "This browser doesn't seem to support the `files` property of file inputs.";
            $("#AlertMessageBox").dialog("open");
        } else {
            var ImageFile = input.files[0];
            var filename = input.value;

            readImageContent(ImageFile).then(function(result) {
                var standardImageOutput_initial = document.getElementById('StandardImageOutput_initial');
                standardImageOutput_initial.src = result;
                $("#StandardImageOutput_initial").show();
                $("#StandardProcessingModelSelectDescription").show();
                $("#StandardProcessingModelSelect").show();
                $("#StandardImageUploadDescription").show();
                $("#StandardImageUploadButton").show();
            });
        }
    });

    $("#StandardImageUploadButton").click(function() {
        // Check to ensure that the file API is supported in the user's browser
        if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
            //alert('The File APIs are not fully supported in this browser.');
            document.getElementById("AlertMessageBoxText").innerHTML = "The File APIs are not fully supported in this browser.";
            $("#AlertMessageBox").dialog("open");
            return;
        }

        var input = document.getElementById("StandardImageUploadFile");
        if (!input) {
            //alert("File could not be found");
            document.getElementById("AlertMessageBoxText").innerHTML = "File could not be found";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files) {
            //alert("This browser doesn't seem to support the `files` property of file inputs.");
            document.getElementById("AlertMessageBoxText").innerHTML = "This browser doesn't seem to support the `files` property of file inputs.";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files[0]) {
            //alert("Please select a Beer.xml file to import!");
            document.getElementById("AlertMessageBoxText").innerHTML = "Please select an image to process!!";
            $("#AlertMessageBox").dialog("open");
        } else {
            var ImageFile = input.files[0];
            var name = input.value.split('\\').pop().split('.');
            STANDARD_FILE_EXTENSION = name.pop();
            STANDARD_FILE_NAME = name.pop();
            let inferenceMode = document.getElementById('StandardProcessingModelSelect').value;

            readImageContent(ImageFile).then(function(result) {
                SendImageForStandardProcessing(result,STANDARD_FILE_EXTENSION,inferenceMode);
            });
        }
    });

    $("#SaveStandardProcessedImageButton").click(function() {
        if (STANDARD_FILE_NAME !== "" && STANDARD_FILE_EXTENSION !== "") {
            let link = document.createElement('a');
            var processedImage = document.getElementById("StandardImageOutput_processed");
            link.download = STANDARD_FILE_NAME + '_processed.' + STANDARD_FILE_EXTENSION;
            link.href = processedImage.src;
            link.click();
        }
    });



    $("#GrabcutModificationCanvas").mousedown(function(event) {
        if (CANVAS_MODE == "box") {
            // We need to:
            // - Record the location of the clicks
            // - record the number of clicks
            coordinateX = event.offsetX;
            coordinateY = event.offsetY;

            switch(NUMBER_CANVAS_BOUNDINGBOX_CLICKS) {

                case 0: // This is the first click of the session
                    click0 = ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[0];
                    click0[0] = coordinateX;
                    click0[1] = coordinateY;
                    ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[0] = click0;
                    NUMBER_CANVAS_BOUNDINGBOX_CLICKS += 1;
                    break;
                case 1: // This is the 2nd click
                    click1 = ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[1];
                    click1[0] = coordinateX;
                    click1[1] = coordinateY;
                    ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[1] = click1;
                    NUMBER_CANVAS_BOUNDINGBOX_CLICKS += 1;
                    break;
                case 2:
                    click2 = ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[2];
                    click2[0] = coordinateX;
                    click2[1] = coordinateY;
                    ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[2] = click2;
                    NUMBER_CANVAS_BOUNDINGBOX_CLICKS += 1;
                    break;
                case 3:
                    click3 = ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[3];
                    click3[0] = coordinateX;
                    click3[1] = coordinateY;
                    ACTIVE_BOUNDINGBOX_CLICK_COORDINATES[3] = click3;
                    NUMBER_CANVAS_BOUNDINGBOX_CLICKS += 1;
                    BOUNDINGBOX_SET = true;
                    drawBoundingBox(ACTIVE_BOUNDINGBOX_CLICK_COORDINATES);
                    break;
                default:
                    break;
            }

        } else {
            isDrawing = true;
        }
        
    });

    function drawBoundingBox(clickCoordinates) {

        smallestX = 10000;
        smallestY = 10000;
        largestX = -1;
        largestY = -1;

        // Find the smallest and largest X, and the smallest and largest Y
        for (let i = 0; i < clickCoordinates.length; i++) {
            curCoordinate = clickCoordinates[i];
            curX = curCoordinate[0];
            curY = curCoordinate[1];

            if (curX < smallestX) {
                smallestX = curX;
            } 
            
            if (curX > largestX) {
                largestX = curX;
            } 

            if (curY < smallestY) {
                smallestY = curY;
            } 
            
            if (curY > largestY) {
                largestY = curY;
            } 
        }

        ACTIVE_GRABCUT_BOUNDING_BOX = [smallestX, smallestY, largestX, largestY];

        // Red box
        canvasContext.beginPath();
        canvasContext.lineWidth = "4";
        canvasContext.strokeStyle = "green";
        canvasContext.rect(smallestX, smallestY, (largestX - smallestX), (largestY-smallestY));
        canvasContext.stroke();
    }

    $("#GrabcutModificationCanvas").mouseup(function() {
        isDrawing = false;
    });

    $("#GrabcutModificationCanvas").mousemove(function(event) {
        draw(event.offsetX, event.offsetY)
    });

    $("#GrabcutOptionSelect").change(function() {
        let selectedValue = document.getElementById('GrabcutOptionSelect').value;

        switch(selectedValue) {
            case "0":
                CANVAS_MODE = "box"
                break;
            case "1":
                CANVAS_MODE = "foreground"
                canvasContext.fillStyle = "red";
                if (!BOUNDINGBOX_SET) {
                    NUMBER_CANVAS_BOUNDINGBOX_CLICKS = 0;
                }
                break;
            case "2":
                CANVAS_MODE = "background"
                canvasContext.fillStyle = "blue";
                if (!BOUNDINGBOX_SET) {
                    NUMBER_CANVAS_BOUNDINGBOX_CLICKS = 0;
                }
                break;
        }
    });

    $("GrabcutModeSelect").change(function() {

        let selectedValue = document.getElementById('GrabcutModeSelect').value;

        switch(selectedValue) {
            case "0":
                ACTIVE_GRABCUT_SESSION_MODE = "basic";
                // UI stuff for basic mode

                // Hide elements that no longer belong

                // Show elements that are now relevant

                break;
            case "1":
                ACTIVE_GRABCUT_SESSION_MODE = "advanced";
                // UI stuff for advanced mode

                // Hide elements that no longer belong

                // Show elements that are now relevant

                break;
        }

    });

    $("#GrabcutImageUploadFile").change(function() {
        // Check to ensure that the file API is supported in the user's browser
        if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
            //alert('The File APIs are not fully supported in this browser.');
            document.getElementById("AlertMessageBoxText").innerHTML = "The File APIs are not fully supported in this browser.";
            $("#AlertMessageBox").dialog("open");
            return;
        }

        var input = document.getElementById("GrabcutImageUploadFile");
        if (!input) {
            //alert("File could not be found");
            document.getElementById("AlertMessageBoxText").innerHTML = "File could not be found";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files) {
            //alert("This browser doesn't seem to support the `files` property of file inputs.");
            document.getElementById("AlertMessageBoxText").innerHTML = "This browser doesn't seem to support the `files` property of file inputs.";
            $("#AlertMessageBox").dialog("open");
        } else {
            var ImageFile = input.files[0];
            var filename = input.value;

            readImageContent(ImageFile).then(function(result) {
                $("#GrabcutModeSelectDescription").show();
                $("#GrabcutModeSelect").show();
                document.getElementById('GrabcutModeSelect').disabled = false;

                $("#GrabcutInstructions").show();
                $("#GrabcutOptionSelect").show();
                $("#ClearInstructions").show();
                $("#ClearGrabcutCanvasButton").show();
                $("#GrabcutProcessImageDescription").show();
                $("#GrabcutImageUploadButton").show();
                $("#ClearGrabcutButtonDescription").show();
                $("#ClearGrabcutButton").show();
                //set up the interval
                var thisInterval = setInterval(function() {
                    //this if statment checks if the id "thisCanvas" is linked to something
                    if(document.getElementById('GrabcutModificationCanvas') != null) {
                        canvasActive = true;
                        var canvasBackgroundImage = document.getElementById('CanvasBackgroundImage');
                        canvasBackgroundImage.src = result;
                        $("#CanvasBackgroundImage").show();
                        
                        //clearInterval() will remove the interval if you have given your interval a name.
                        clearInterval(thisInterval)
                    }
                },500); // loops every .5 sec
            });
        }
    });

    $("#ClearGrabcutCanvasButton").click(function() {
        if(confirm("This will clear your current highlighted areas, proceed?")) {
            canvasContext.clearRect(0,0, canvas.width, canvas.height);
            NUMBER_CANVAS_BOUNDINGBOX_CLICKS = 0;
            BOUNDINGBOX_SET = false;
            ACTIVE_BOUNDINGBOX_CLICK_COORDINATES = [[0, 0], [0, 0], [0, 0], [0, 0]];
        }
    });

    $("#GrabcutImageUploadButton").click(function() {
        // Check to ensure that the file API is supported in the user's browser
        if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
            //alert('The File APIs are not fully supported in this browser.');
            document.getElementById("AlertMessageBoxText").innerHTML = "The File APIs are not fully supported in this browser.";
            $("#AlertMessageBox").dialog("open");
            return;
        }

        var input = document.getElementById("GrabcutImageUploadFile");
        if (!input) {
            //alert("File could not be found");
            document.getElementById("AlertMessageBoxText").innerHTML = "File could not be found";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files) {
            //alert("This browser doesn't seem to support the `files` property of file inputs.");
            document.getElementById("AlertMessageBoxText").innerHTML = "This browser doesn't seem to support the `files` property of file inputs.";
            $("#AlertMessageBox").dialog("open");
        } else if (!BOUNDINGBOX_SET) {
            document.getElementById("AlertMessageBoxText").innerHTML = "You must set a bounding box to continue.";
            $("#AlertMessageBox").dialog("open");
        } else {

            var ImageFile = input.files[0];
            var filename = input.value;

            var grabcutMode = document.getElementById("GrabcutModeSelect").value;

            switch(ACTIVE_GRABCUT_SESSION_MODE) {
                case "basic": // Basic
                    // Need to send:
                    // - raw image
                    // - human hints mask with white = foreground, black = background, and rest filled with grey
                    // ** Is it easier to create an all white image and include it with the backend code? Or in backend?

                    readImageContent(ImageFile).then(function(result) {

                        var thisInterval = setInterval(function() {
                            //this if statment checks if the id "thisCanvas" is linked to something
                            if(document.getElementById('GrabcutModificationCanvas') != null) {
                                
                                if (!ACTIVE_GRABCUT_SESSION) {
                                    // TODO: Get the bounding box
                                    ACTIVE_GRABCUT_SESSION = true;
                                    ACTIVE_GRABCUT_SESSION_MODE = "basic";
                                }

                                // TODO: Call a function here to convert the image overlay pixels into gray / white / black mask
                                let canvasImageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height)
                                let { data } = canvasImageData;

                                let augmentedMask = fillInCanvasObject();

                                canvasImageData.data = augmentedMask;
                                canvasContext.putImageData(canvasImageData, 0, 0);

                                // Need to get the overlay image out of the canvas object
                                let overlayFormat = "jpeg";
                                let canvasImageOverlay = canvas.toDataURL("image/" + overlayFormat);
                                canvasImageData.data = data;
                                canvasContext.putImageData(canvasImageData, 0, 0);

                                // Get some details about the actual image
                                let name = input.value.split('\\').pop().split('.');
                                GRABCUT_FILE_EXTENSION = name.pop();
                                GRABCUT_FILE_NAME = name.pop();

                                document.getElementById('GrabcutModeSelect').disabled = true;
        
                                var canvasBackgroundImage = document.getElementById('CanvasBackgroundImage');
                                

                                // Need to send the overlay image and the src image for processing

                                // swapped result.
                                SendImageForGrabcutProcessing(canvasBackgroundImage.src, GRABCUT_FILE_EXTENSION, canvasImageOverlay, overlayFormat, canvas.width, canvas.height, ACTIVE_GRABCUT_BOUNDING_BOX, ACTIVE_GRABCUT_SESSION_MODE, GRABCUT_COUNT, ACTIVE_GRABCUT_SESSION_KEY);
        
                                //clearInterval() will remove the interval if you have given your interval a name.
                                clearInterval(thisInterval)
                            }
                        },500); // loops every .5 sec
                    });

                    break;
                
                case "advanced": // Advanced - Need to implement
                    break
            }
        }
    });

    $("#ClearStandardButton").click(function() {
        if (confirm("Are you sure you would like to reset your current Inference session?")) {
            document.getElementById('StandardImageUploadFile').value = "";
            document.getElementById('StandardImageOutput_initial').src = "";
            $("#StandardImageOutput_initial").hide("fast");
            $("#StandardProcessingModelSelectDescription").hide("fast");
            $("#StandardProcessingModelSelect").hide("fast");
            $("#StandardImageUploadDescription").hide("fast");
            $("#StandardImageUploadButton").hide("fast");
            document.getElementById('StandardImageOutput_processed').src = "";
            $("#StandardImageOutput_processed").hide("fast");
            $("#StandardProcessedImageDescription").hide("fast");
            $("#SaveStandardProcessedImageButton").hide("fast");
            $("#ClearStandardButtonDescription").hide("fast");
            $("#ClearStandardButton").hide("fast");
        }
    });

    $("#ClearGrabcutButton").click(function() {
        if (confirm("Are you sure you would like to reset your current Grab-Cut session?")) {
            ClearGrabcutSession();
        }
    });

    $("#ClearBatchButton").click(function() {

        document.getElementById("BatchImageUploadDirectory").value = "";

        $("#BatchProcessingModelSelectDescription").hide("fast");
        $("#BatchProcessingModelSelect").hide("fast");
        $("#BatchImageUploadDescription").hide("fast");
        $("#BatchImageUploadButton").hide("fast");
        $("ClearBatchButton").hide("fast");
    });


    $("#SaveGrabcutProcessedImageButton").click(function() {
        if (GRABCUT_FILE_NAME !== "" && GRABCUT_FILE_EXTENSION !== "") {
            let link = document.createElement('a');
            var processedImage = document.getElementById("GrabcutImageOutput_processed");
            link.download = GRABCUT_FILE_NAME + '_processed_' + GRABCUT_COUNT + '.' + GRABCUT_FILE_EXTENSION;
            link.href = processedImage.src;
            link.click();
        }
    });



    $("#BatchImageUploadDirectory").change(function() {
        $("#BatchProcessingModelSelectDescription").show();
        $("#BatchProcessingModelSelect").show();
        $("#BatchImageUploadDescription").show();
        $("#BatchImageUploadButton").show();
        $("#ClearBatchButton").show();
    });

    $("#BatchImageUploadButton").click(function() {
        // Check to ensure that the file API is supported in the user's browser
        if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
            //alert('The File APIs are not fully supported in this browser.');
            document.getElementById("AlertMessageBoxText").innerHTML = "The File APIs are not fully supported in this browser.";
            $("#AlertMessageBox").dialog("open");
            return;
        }

        var input = document.getElementById("BatchImageUploadDirectory");
        if (!input) {
            //alert("File could not be found");
            document.getElementById("AlertMessageBoxText").innerHTML = "Directory could not be found";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files) {
            //alert("This browser doesn't seem to support the `files` property of file inputs.");
            document.getElementById("AlertMessageBoxText").innerHTML = "This browser doesn't seem to support the `files` property of file inputs.";
            $("#AlertMessageBox").dialog("open");
        } else if (!input.files[0]) {
            //alert("Please select a Beer.xml file to import!");
            document.getElementById("AlertMessageBoxText").innerHTML = "Please select an image to process!!";
            $("#AlertMessageBox").dialog("open");
        } else {

            let id = Date.now();

            var numFiles = input.files.length;

            var counter = 0;

            var curBatchRecord = {
                id: id,
                currentProcessedCount: 0,
                totalCount: 0,
                images: []
            }

            var inferenceMode = document.getElementById('BatchProcessingModelSelect').value;

            for (i = 0; i < numFiles; i++) {
                let ImageFile = input.files[i];
                let filename = ImageFile.name;
                let filetype = ImageFile.type.split('/').pop();
                let relativePath = ImageFile.webkitRelativePath.split('/');
                let file = relativePath.pop();
                let directoryName = relativePath.pop();

                if (ImageFile.type === "image/jpeg" || ImageFile.type === "image/png") {
                    counter += 1;

                    console.log(ImageFile);
                    var image = {
                        id: id,
                        subId: counter,
                        directoryName: directoryName,
                        fileName: filename,
                        type: filetype
                    }
                    curBatchRecord.images.push(image);
                    curBatchRecord.totalCount += 1;
                }
            }

            BATCHES.records.push(curBatchRecord);
            BATCHES.count += 1;

            let CurBatch = BATCHES.records.find(x => x.id == id);

            for (i = 0; i < numFiles; i++) {
                let ImageFile = input.files[i];
                let filetype = ImageFile.type.split('/').pop();
                let imageName = ImageFile.name;

                if (ImageFile.type === "image/jpeg" || ImageFile.type === "image/png") {
                    readImageContent(ImageFile).then(function(result) {
                        let curImageRecord = CurBatch.images.find(x => x.fileName == imageName);
                        SendImageForStandardBatchProcessing(result,filetype,id,curImageRecord.subId,inferenceMode);
                    });
                }
            }
        }
    });



    $("#AlertMessageBox").dialog({
        modal: true,
        buttons: {
            Ok: function() {
                $(this).dialog("close");
            }
        },
        autoOpen: false
    });

    $("#button_m1").click(function() {
        $("#Container2").hide("fast");
        $("#Container3").hide("fast");
        $("#Container4").hide("fast");
        // $("#Container5").hide("fast");
        // $("#Container6").hide("fast");

        $("#Container1").show("fast");

        $("#NavItemM1").css("border-bottom-style", "solid");
        $("#NavItemM2").css("border-bottom-style", "none");
        $("#NavItemM3").css("border-bottom-style", "none");
        $("#NavItemM4").css("border-bottom-style", "none");
        // $("#NavItemM5").css("border-bottom-style", "none");
        // $("#NavItemM6").css("border-bottom-style", "none");

        document.getElementById("collapsibleNavbar_M").className = "navbar-collapse justify-content-start collapse";
    });

    $("#button_m2").click(function() {
        $("#Container1").hide("fast");
        $("#Container3").hide("fast");
        $("#Container4").hide("fast");
        // $("#Container5").hide("fast");
        // $("#Container6").hide("fast");

        $("#Container2").show("fast");

        $("#NavItemM1").css("border-bottom-style", "none");
        $("#NavItemM2").css("border-bottom-style", "solid");
        $("#NavItemM3").css("border-bottom-style", "none");
        $("#NavItemM4").css("border-bottom-style", "none");
        // $("#NavItemM5").css("border-bottom-style", "none");
        // $("#NavItemM6").css("border-bottom-style", "none");

        document.getElementById("collapsibleNavbar_M").className = "navbar-collapse justify-content-start collapse";
    });

    $("#button_m3").click(function() {
        $("#Container1").hide("fast");
        $("#Container2").hide("fast");
        $("#Container4").hide("fast");
        // $("#Container5").hide("fast");
        // $("#Container6").hide("fast");

        $("#Container3").show("fast");

        $("#NavItemM1").css("border-bottom-style", "none");
        $("#NavItemM2").css("border-bottom-style", "none");
        $("#NavItemM3").css("border-bottom-style", "solid");
        $("#NavItemM4").css("border-bottom-style", "none");
        // $("#NavItemM5").css("border-bottom-style", "none");
        // $("#NavItemM6").css("border-bottom-style", "none");

        document.getElementById("collapsibleNavbar_M").className = "navbar-collapse justify-content-start collapse";
    });

    $("#button_m4").click(function() {
        $("#Container1").hide("fast");
        $("#Container2").hide("fast");
        $("#Container3").hide("fast");
        // $("#Container5").hide("fast");
        // $("#Container6").hide("fast");

        $("#Container4").show("fast");

        $("#NavItemM1").css("border-bottom-style", "none");
        $("#NavItemM2").css("border-bottom-style", "none");
        $("#NavItemM3").css("border-bottom-style", "none");
        $("#NavItemM4").css("border-bottom-style", "solid");
        // $("#NavItemM5").css("border-bottom-style", "none");
        // $("#NavItemM6").css("border-bottom-style", "none");

        document.getElementById("collapsibleNavbar_M").className = "navbar-collapse justify-content-start collapse";
    });

    // $("#button_m5").click(function() {
    //     $("#Container1").hide("fast");
    //     $("#Container2").hide("fast");
    //     $("#Container3").hide("fast");
    //     $("#Container4").hide("fast");
    //     // $("#Container6").hide("fast");

    //     $("#Container5").show("fast");

    //     $("#NavItemM1").css("border-bottom-style", "none");
    //     $("#NavItemM2").css("border-bottom-style", "none");
    //     $("#NavItemM3").css("border-bottom-style", "none");
    //     $("#NavItemM4").css("border-bottom-style", "none");
    //     $("#NavItemM5").css("border-bottom-style", "solid");
    //     // $("#NavItemM6").css("border-bottom-style", "none");

    //     document.getElementById("collapsibleNavbar_M").className = "navbar-collapse justify-content-start collapse";
    // });

    // $("#button_m6").click(function() {
    //     $("#Container1").hide("fast");
    //     $("#Container2").hide("fast");
    //     $("#Container3").hide("fast");
    //     $("#Container4").hide("fast");
    //     $("#Container5").hide("fast");
        
    //     $("#Container6").show("fast");

    //     $("#NavItemM1").css("border-bottom-style", "none");
    //     $("#NavItemM2").css("border-bottom-style", "none");
    //     $("#NavItemM3").css("border-bottom-style", "none");
    //     $("#NavItemM4").css("border-bottom-style", "none");
    //     $("#NavItemM5").css("border-bottom-style", "none");
    //     $("#NavItemM6").css("border-bottom-style", "solid");

    //     document.getElementById("collapsibleNavbar_M").className = "navbar-collapse justify-content-start collapse";
    // });

    // -------------- End Element Handlers ------------------
    // ------------------------------------------------------

    // ----------------- Misc Functions ---------------------
    // ------------------------------------------------------

    /**
     * 
     */
    function LoadInitialContent() {
         
    }

    /**
     * Reads an image file into its Base64 representation
     * @param {*} file - Image file to translate into Base64
     * @returns - Base64 string representation of the image file parameter
     */
    function readImageContent(file) {
        return new Promise(function(resolve, reject) {
            let fr = new FileReader()
            fr.onload = function() {
                resolve(this.result)
            }
            fr.readAsDataURL(file);
        });
    }

    /**
     * Bundles the given batch records into a zip file and downloads the zip to user's machine
     * @param {*} batch - The batch record to find and zip
     */
    function bundleZipFile(batch) {
        let numberImages = batch.totalCount;

        let directories = [];
        for (i = 0; i < numberImages; i++) {
            let curImage = batch.images[i];
            curImageDirectory = curImage.directoryName;
            if (!directories.includes(curImageDirectory)) {
                directories.push(curImageDirectory);
            }
        }

        // Get the images from each directory and
        for (i = 0; i < directories.length; i ++) {

            // Create a zip file for the current directory
            let curDirectoryName = directories[i];
            let zip = new JSZip();

            // Add all images from the directory into the zip file, download
            let curDirectoryImages = batch.images.filter(x => x.directoryName == directories[i]);
            for (j = 0; j < curDirectoryImages.length; j++) {
                let curImage = curDirectoryImages[j];
                let curImageName = curImage.fileName.split('.')[0];
                let finalName = curImageName + "_processed." + curImage.fileName.split('.')[1];
                let binaryData = curImage.src.split(',')[1];
                zip.file(finalName, binaryData, {base64: true});
            }

            // Save and Download the zip file now that all images are in
            zip.generateAsync({type: "blob"}).then(function(content) {
                saveAs(content, curDirectoryName+"_processed");
            });
        }

    }

    function fillInCanvasObject() {
        let canvasWidth = canvas.width;
        let canvasHeight = canvas.height;

        let canvasImageData = canvasContext.getImageData(0, 0, canvasWidth, canvasHeight)
        let { data } = canvasImageData;
        let { length } = data;

        let newData = data;

        console.log(data);

        for (let i = 0; i < length; i+= 4) {
            let r = data[i + 0];
            let g = data[i + 1];
            let b = data[i + 2];
            let a = data[i + 3];

            let newR = r;
            let newG = g;
            let newB = b;
            let newA = a;

            if (r == 255 && g == 0 && b == 0) {
                newR = 255;
                newG = 255;
                newB = 255;
                newA = a;
            } else if (r == 0 && g == 0 && b == 255) {
                newR = 0;
                newG = 0;
                newB = 0;
                newA = a;
            } else {
                newR = 128;
                newG = 128;
                newB = 128;
                newA = a;
            }

            newData[i + 0] = newR;
            newData[i + 1] = newG;
            newData[i + 2] = newB;
            newData[i + 3] = newA;
        }

        console.log(newData);
        return newData;
    }

    /**
     * Takes in coordinates of user interaction on the canvas and draws the corresponding line
     * @param {*} x - X coordinate for action
     * @param {*} y - Y coordinate for action
     */
    function draw(x, y) {
        if (canvasActive) {
            if (isDrawing) {
                canvasContext.beginPath();
                canvasContext.arc(x, y, 10, 0, Math.PI*2);
                canvasContext.closePath();
                canvasContext.fill();
            }
        }
    }

    // --------------- End Misc Functions -------------------
    // ------------------------------------------------------

    // ---------------------- Main --------------------------
    // ------------------------------------------------------

    LoadInitialContent();

    // -------------------- End Main ------------------------
    // ------------------------------------------------------
});