let totalSeconds = 60 * 180; 

function updateTimer() {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  document.getElementById("timer").textContent = 
    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

  if (totalSeconds <= 0) {
    
    showTimerExpiredModal();

    setTimeout(() => {
      redirectToStart();
    }, 8000);
  } else {
    totalSeconds--;
    setTimeout(updateTimer, 1000);
  }
}

window.onload = updateTimer;