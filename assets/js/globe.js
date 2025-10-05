// Limit zoom levels
const minHeight = 5_000_000;   // ~5,000 km above Earth
const maxHeight = 50_000_000;  // ~50,000 km above Earth

viewer.scene.camera.moveEnd.addEventListener(function () {
  const cameraHeight = Cesium.Cartographic.fromCartesian(
    viewer.scene.camera.position
  ).height;

  if (cameraHeight < minHeight) {
    viewer.scene.camera.moveBackward(minHeight - cameraHeight);
  } else if (cameraHeight > maxHeight) {
    viewer.scene.camera.moveForward(cameraHeight - maxHeight);
  }
});

let countriesLayer, provincesLayer;

Promise.all([
  Cesium.GeoJsonDataSource.load("countries.geo.json"),
  Cesium.GeoJsonDataSource.load("provinces.geo.json")
]).then(function (sources) {
  countriesLayer = sources[0];
  provincesLayer = sources[1];

  viewer.dataSources.add(countriesLayer);
  viewer.dataSources.add(provincesLayer);

  // Start with provinces hidden
  provincesLayer.show = false;

  // Style them (same loop as before)
  [countriesLayer, provincesLayer].forEach(ds => {
    ds.entities.values.forEach(entity => {
      if (entity.polygon) {
        entity.polygon.material = Cesium.Color.fromCssColorString("#111111");
        entity.polygon.outline = true;
        entity.polygon.outlineColor = Cesium.Color.WHITE;
      }
    });
  });

  viewer.zoomTo(countriesLayer);
});

// Toggle visibility based on zoom
viewer.scene.camera.changed.addEventListener(function () {
  const height = Cesium.Cartographic.fromCartesian(
    viewer.scene.camera.position
  ).height;

  if (height < 10_000_000) {
    // zoomed in → show provinces
    if (provincesLayer) provincesLayer.show = true;
    if (countriesLayer) countriesLayer.show = false;
  } else {
    // zoomed out → show only countries
    if (provincesLayer) provincesLayer.show = false;
    if (countriesLayer) countriesLayer.show = true;
  }
});
