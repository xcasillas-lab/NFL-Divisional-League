
(function(){
  /* 2026 NFL season kickoff: Sept. 9, 2026 at 7:20 PM Central Daylight Time (UTC-05:00). */
  var kickoff = new Date('2026-09-09T19:20:00-05:00');
  var daysEl = document.getElementById('countdown-days');
  var hoursEl = document.getElementById('countdown-hours');
  var minutesEl = document.getElementById('countdown-minutes');
  var secondsEl = document.getElementById('countdown-seconds');

  function pad(value){ return String(value).padStart(2, '0'); }

  function updateSeasonCountdown(){
    var remaining = kickoff.getTime() - Date.now();

    if(remaining <= 0){
      daysEl.textContent = '00';
      hoursEl.textContent = '00';
      minutesEl.textContent = '00';
      secondsEl.textContent = '00';
      var label = document.querySelector('.season-countdown-copy strong');
      if(label) label.textContent = 'The 2026 Season Is Underway!';
      return;
    }

    var totalSeconds = Math.floor(remaining / 1000);
    var days = Math.floor(totalSeconds / 86400);
    var hours = Math.floor((totalSeconds % 86400) / 3600);
    var minutes = Math.floor((totalSeconds % 3600) / 60);
    var seconds = totalSeconds % 60;

    daysEl.textContent = pad(days);
    hoursEl.textContent = pad(hours);
    minutesEl.textContent = pad(minutes);
    secondsEl.textContent = pad(seconds);
  }

  updateSeasonCountdown();
  setInterval(updateSeasonCountdown, 1000);
})();
