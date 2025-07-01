// Song data
const songs = [
    { title: "Yen Kanukulla Oru Siriki", filePath: "songs/song.mp3", coverPath: "images/cover0.jpeg" },
    { title: "Cielo - Huma-Huma", filePath: "songs/song1.mp3", coverPath: "images/cover1.jpeg" },
    { title: "DEAF KEV - Invincible", filePath: "songs/song2.mp3", coverPath: "images/cover2.jpeg" },
    { title: "Different Heaven & EH!DE - My Heart", filePath: "songs/song3.mp3", coverPath: "images/cover3.jpeg" },
    { title: "Janji - Heroes Tonight", filePath: "songs/song4.mp3", coverPath: "images/cover4.jpeg" }
    // Add more songs as needed
  ];
  
  // Variables
  let songIndex = 0;
  let audioElement = new Audio(songs[songIndex].filePath);
  const masterPlay = document.getElementById("masterPlay");
  const previousBtn = document.getElementById("previous");
  const nextBtn = document.getElementById("next");
  const progressBar = document.getElementById("progressBar");
  const masterSongName = document.getElementById("masterSongName");
  const gif = document.getElementById("gif");
  const songListContainer = document.getElementById("songList");
  
  // Load song list dynamically
  function loadSongList() {
    songs.forEach((song, i) => {
      const div = document.createElement("div");
      div.classList.add("songItem");
      div.setAttribute("data-index", i);
      div.innerHTML = `
        <img src="${song.coverPath}" alt="Cover ${i}" />
        <span class="songName">${song.title}</span>
        <span class="songlistplay">
          <span class="timestamp">03:30 <i class="far fa-play-circle songItemPlay" id="${i}"></i></span>
        </span>
      `;
      songListContainer.appendChild(div);
    });
  }
  loadSongList();
  
  // Play song function
  function playSong(index) {
    songIndex = index;
    audioElement.src = songs[songIndex].filePath;
    audioElement.currentTime = 0;
    audioElement.play();
    masterSongName.textContent = songs[songIndex].title;
    masterPlay.classList.replace("fa-play-circle", "fa-pause-circle");
    gif.style.opacity = 1;
    updatePlayButtons();
  }
  
  // Pause song function
  function pauseSong() {
    audioElement.pause();
    masterPlay.classList.replace("fa-pause-circle", "fa-play-circle");
    gif.style.opacity = 0;
    updatePlayButtons();
  }
  
  // Update the play icons on the list
  function updatePlayButtons() {
    document.querySelectorAll(".songItemPlay").forEach(btn => {
      const btnIndex = parseInt(btn.id, 10);
      if (!audioElement.paused && btnIndex === songIndex) {
        btn.classList.replace("fa-play-circle", "fa-pause-circle");
      } else {
        btn.classList.replace("fa-pause-circle", "fa-play-circle");
      }
    });
  }
  
  // Toggle play/pause from master button
  masterPlay.addEventListener("click", () => {
    if (audioElement.paused) {
      playSong(songIndex);
    } else {
      pauseSong();
    }
  });
  
  // Play song on clicking list icon
  document.querySelectorAll(".songItemPlay").forEach(button => {
    button.addEventListener("click", (e) => {
      const index = parseInt(e.target.id, 10);
      if (songIndex === index && !audioElement.paused) {
        pauseSong();
      } else {
        playSong(index);
      }
    });
  });
  
  // Update progress bar as song plays
  audioElement.addEventListener("timeupdate", () => {
    const progress = parseInt((audioElement.currentTime / audioElement.duration) * 100) || 0;
    progressBar.value = progress;
  });
  
  // Seek audio when progress bar changes
  progressBar.addEventListener("input", () => {
    audioElement.currentTime = (progressBar.value * audioElement.duration) / 100;
  });
  
  // Previous song button
  previousBtn.addEventListener("click", () => {
    songIndex = (songIndex - 1 + songs.length) % songs.length;
    playSong(songIndex);
  });
  
  // Next song button
  nextBtn.addEventListener("click", () => {
    songIndex = (songIndex + 1) % songs.length;
    playSong(songIndex);
  });
  
  // When song ends, auto play next
  audioElement.addEventListener("ended", () => {
    nextBtn.click();
  });
  