// Erlaubt das Ablegen im Drop-Bereich
function dragOverHandler(event) {
  event.preventDefault();
  event.currentTarget.classList.add('hover');
}



// Bild anzeigen, nachdem es geladen wurde
function displayImage(file) {
  const img = document.getElementById('detected-image');
  img.style.display = 'block';

//Selbst hinzugefügt 2Z
    img.onload = function() {
        getImageSize();
    };

  const reader = new FileReader();
  reader.onload = function (event) {
    img.src = event.target.result;
  };
  reader.readAsDataURL(file);

}

function getImageSize() {

	  const img = document.getElementById('detected-image');
      const width = img.naturalWidth; // Originalbreite des Bildes
      const height = img.naturalHeight; // Originalhöhe des Bildes
            
      // Ausgabe der Bildgröße
      document.getElementById('imageSize').innerText = `(${width} x ${height} Pixel)`;
}