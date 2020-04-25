var initialized = false;
var detect = true;
var takePhoto = false;

function stop_detecting() {
    detect = false;
}

function use_image() {
    takePhoto = true;
}

function start_face_search() {
    /*
        (0) check whether we're already running face detection
    */
    detect = true;
    if (initialized)
        return; // if yes, then do not initialize everything again
    /*
        (1) initialize the pico.js face detector
    */
    var update_memory = pico.instantiate_detection_memory(5); // we will use the detecions of the last 5 frames
    var facefinder_classify_region = function (r, c, s, pixels, ldim) {
        return -1.0;
    };
    var cascadeurl =
        'https://raw.githubusercontent.com/nenadmarkus/pico/c2e81f9d23cc11d1a612fd21e4f9de0921a5d0d9/rnt/cascades/facefinder';
    fetch(cascadeurl).then(function (response) {
        response.arrayBuffer().then(function (buffer) {
            var bytes = new Int8Array(buffer);
            facefinder_classify_region = pico.unpack_cascade(bytes);
            console.log('* facefinder loaded');
        })
    })
    /*
        (3) get the drawing context on the canvas and define a function to transform an RGBA image to grayscale
    */
    var can = document.getElementById('video')
    var ctx = can.getContext('2d');

    function rgba_to_grayscale(rgba, nrows, ncols) {
        var gray = new Uint8Array(nrows * ncols);
        for (var r = 0; r < nrows; ++r)
            for (var c = 0; c < ncols; ++c)
                // gray = 0.2*red + 0.7*green + 0.1*blue
                gray[r * ncols + c] = (2 * rgba[r * 4 * ncols + 4 * c + 0] + 7 * rgba[r * 4 * ncols + 4 * c + 1] + 1 *
                    rgba[r * 4 * ncols + 4 * c + 2]) / 10;
        return gray;
    }
    /*
        (4) this function is called each time a video frame becomes available
    */
    var processfn = function (video, dt) {
        if (!detect) {
            return;
        }

        // render the video frame to the canvas element and extract RGBA pixel data
        ctx.drawImage(video, 0, 0);
        var rgba = ctx.getImageData(0, 0, 640, 480).data;

        // prepare input to `run_cascade`
        image = {
            "pixels": rgba_to_grayscale(rgba, 480, 640),
            "nrows": 480,
            "ncols": 640,
            "ldim": 640
        }
        params = {
            "shiftfactor": 0.1, // move the detection window by 10% of its size
            "minsize": 100, // minimum size of a face
            "maxsize": 1000, // maximum size of a face
            "scalefactor": 1.1 // for multiscale processing: resize the detection window by 10% when moving to the higher scale
        }
        // run the cascade over the frame and cluster the obtained detections
        // dets is an array that contains (r, c, s, q) quadruplets
        // (representing row, column, scale and detection score)
        dets = pico.run_cascade(image, facefinder_classify_region, params);
        dets = update_memory(dets);
        dets = pico.cluster_detections(dets, 0.2); // set IoU threshold to 0.2

        // draw detections
        var numFaces = 0;
        for (i = 0; i < dets.length; ++i) {
            // check the detection scores
            // if it's above the threshold, draw it
            // (the constant 50.0 is empirical: other cascades might require a different one)
            if (dets[i][3] > 50.0) {
                ++numFaces;
                ctx.beginPath();
                ctx.arc(dets[i][1], dets[i][0], dets[i][2] / 2, 0, 2 * Math.PI, false);
                ctx.lineWidth = 3;
                ctx.strokeStyle = 'red';
                ctx.stroke();
            }
        }

        // Set Hidden Form field to face image
        if (numFaces == 1 && takePhoto) {
            takePhoto = false;
            detect = false;

            for (i = 0; i < dets.length; ++i) {
                console.log(dets[i]);
                centerx = dets[i][1];
                centery = dets[i][0];
                diameter = dets[i][2];
                radius = diameter / 2;

                var hidden_canvas = document.createElement('canvas');
                hidden_canvas.width = diameter;
                hidden_canvas.height = diameter;
                var hidden_ctx = hidden_canvas.getContext('2d');

                hidden_ctx.drawImage(can, centerx - radius, centery - radius,
                    diameter, diameter, 0, 0, diameter, diameter);

                document.getElementById('face_image').value = hidden_canvas.toDataURL();
            }
        }
    }
    /*
        (5) instantiate camera handling (see https://github.com/cbrandolino/camvas)
    */
    var mycamvas = new camvas(ctx, processfn);
    /*
        (6) it seems that everything went well
    */
    initialized = true;
}