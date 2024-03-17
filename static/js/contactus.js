document.addEventListener('DOMContentLoaded', function () {
  var center = ol.proj.fromLonLat([77.5946, 12.9716]); // Bangalore, India
  var map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      })
    ],
    view: new ol.View({
      center: center,
      zoom: 13
    })
  });

  document.getElementById('visitBtn').addEventListener('click', function () {
    alert("Schedule a visit feature is not yet implemented.");
  });
});



