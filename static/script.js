let isDragging = false;
const track = document.getElementById("image-track");

window.onmousedown = (e) => {
  isDragging = true;
  track.dataset.mouseDownAt = e.clientX;
};

window.onmouseup = () => {
  isDragging = false;
  track.dataset.mouseDownAt = "0";
  track.dataset.prevPercentage = track.dataset.percentage;
};

window.onmousemove = (e) => {
  if (!isDragging || track.dataset.mouseDownAt == "0") return;

  const mouseDelta = parseFloat(track.dataset.mouseDownAt) - e.clientX;
  const maxDelta = window.innerWidth / 2;

  let percentage = (mouseDelta / maxDelta) * -100;
  let nextPercentage = parseFloat(track.dataset.prevPercentage) + percentage;

  nextPercentage = Math.max(Math.min(nextPercentage, 0), -100);
  track.dataset.percentage = nextPercentage;

  track.animate(
    { transform: `translate(${nextPercentage}%, -50%)` },
    { duration: 1200, fill: "forwards" }
  );
};

const images = document.querySelectorAll('a img');

images.forEach((img) => {
  img.ondragstart = (e) => {
    e.preventDefault();
  };
});

const imageElements = document.querySelectorAll('.image');

imageElements.forEach((image) => {
  image.addEventListener('mouseover', () => {
    const description = image.getAttribute('data-description');
    document.getElementById('description_text').innerText = description;
  });

  image.addEventListener('mouseleave', () => {
    document.getElementById('description_text').innerText = "Hover over an image to see the description."; 
  });
});

