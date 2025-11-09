var originSelect = document.getElementById('origin-select');
var destSelect = document.getElementById('destination-select');
var customDiv = document.getElementById('custom-coords');
var latInput = document.getElementById('custom-lat');
var lonInput = document.getElementById('custom-lon');
var instructionsDiv = document.getElementById('instructions');
var startBtn = document.getElementById('start-btn');

var loadingDiv = document.getElementById('loading-section');
var resultsDiv = document.getElementById('results-section');
var resetBtn = document.getElementById('reset-btn');

var origin = null;
var dest = null;

originSelect.addEventListener('change', function() {
    origin = this.value;
    checkReady();
    showCustomIfNeeded();
});

destSelect.addEventListener('change', function() {
    dest = this.value;
    checkReady();
    showCustomIfNeeded();
});

function showCustomIfNeeded() {
    if (origin === 'C' || dest === 'C') {
        customDiv.style.display = 'block';
    } else {
        customDiv.style.display = 'none';
    }
}

function checkReady() {
    if (origin && dest && origin !== '' && dest !== '') {
        if (origin === dest && origin !== 'R' && origin !== 'C') {
            alert('Pick different locations');
            destSelect.value = '';
            dest = null;
            instructionsDiv.style.display = 'none';
            return;
        }
        
        instructionsDiv.style.display = 'block';
        
        setTimeout(function() {
            instructionsDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    } else {
        instructionsDiv.style.display = 'none';
    }
}

startBtn.addEventListener('click', function() {
    if (!origin || !dest) {
        alert('Select both locations');
        return;
    }
    
    if ((origin === 'C' || dest === 'C') && (!latInput.value || !lonInput.value)) {
        alert('Enter coordinates');
        return;
    }
    
    instructionsDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    
    setTimeout(function() {
        loadingDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
    
    var data = {
        origin: origin,
        destination: dest
    };
    
    if (origin === 'C' || dest === 'C') {
        data.origin_lat = latInput.value;
        data.origin_lon = lonInput.value;
        data.dest_lat = latInput.value;
        data.dest_lon = lonInput.value;
    }
    
    resultsDiv.style.display = 'block';
    var imgs = document.querySelectorAll('.result-img');
    for (var i = 0; i < imgs.length; i++) {
        imgs[i].style.opacity = '0.3';
        imgs[i].style.filter = 'blur(5px)';
    }
    
    var imageFiles = [
        '/static/output/dijkstra_exploration.png',
        '/static/output/dijkstra_path.png',
        '/static/output/astar_exploration.png',
        '/static/output/astar_path.png'
    ];
    
    var checkTimer = setInterval(function() {
        for (var i = 0; i < imageFiles.length; i++) {
            (function(url) {
                var time = Date.now();
                fetch(url + '?t=' + time, { method: 'HEAD' })
                    .then(function(response) {
                        if (response.ok) {
                            var filename = url.split('/').pop().split('.')[0];
                            var images = document.querySelectorAll('img[src*="' + filename + '"]');
                            for (var j = 0; j < images.length; j++) {
                                images[j].src = url + '?t=' + time;
                                images[j].style.opacity = '1';
                                images[j].style.filter = 'none';
                            }
                        }
                    });
            })(imageFiles[i]);
        }
    }, 1000);
    
    fetch('/compute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(function(response) { return response.json(); })
    .then(function(result) {
        clearInterval(checkTimer);
        if (result.success) {
            showResults(result);
        } else {
            alert('Error: ' + (result.error || 'Unknown'));
            loadingDiv.style.display = 'none';
            resultsDiv.style.display = 'none';
            instructionsDiv.style.display = 'block';
        }
    })
    .catch(function(error) {
        clearInterval(checkTimer);
        console.error('Error:', error);
        alert('Error. Try again.');
        loadingDiv.style.display = 'none';
        resultsDiv.style.display = 'none';
        instructionsDiv.style.display = 'block';
    });
});

function showResults(data) {
    document.getElementById('dijkstra-iterations').textContent = data.dijkstra.iterations;
    document.getElementById('dijkstra-distance').textContent = data.dijkstra.distance;
    document.getElementById('dijkstra-time').textContent = data.dijkstra.time;
    
    document.getElementById('astar-iterations').textContent = data.astar.iterations;
    document.getElementById('astar-distance').textContent = data.astar.distance;
    document.getElementById('astar-time').textContent = data.astar.time;
    
    var time = Date.now();
    var allImgs = document.querySelectorAll('.result-img');
    for (var i = 0; i < allImgs.length; i++) {
        var src = allImgs[i].getAttribute('src').split('?')[0];
        allImgs[i].setAttribute('src', src + '?t=' + time);
        allImgs[i].style.opacity = '1';
        allImgs[i].style.filter = 'none';
    }
    
    loadingDiv.style.display = 'none';
    
    setTimeout(function() {
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

resetBtn.addEventListener('click', function() {
    resultsDiv.style.display = 'none';
    
    originSelect.value = '';
    destSelect.value = '';
    customDiv.style.display = 'none';
    latInput.value = '';
    lonInput.value = '';
    instructionsDiv.style.display = 'none';
    
    origin = null;
    dest = null;
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

var modal = document.getElementById('image-modal');
var modalImg = document.getElementById('modal-img');
var modalCaption = document.getElementById('modal-caption');
var closeBtn = document.querySelector('.modal-close');

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('result-img')) {
        modal.style.display = 'block';
        modalImg.src = e.target.src;
        modalCaption.textContent = e.target.alt;
    }
});

closeBtn.addEventListener('click', function() {
    modal.style.display = 'none';
});

modal.addEventListener('click', function(e) {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.style.display === 'block') {
        modal.style.display = 'none';
    }
});
