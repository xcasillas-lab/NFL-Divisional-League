function togglePreseasonRankings(btn){
  const content = document.getElementById('preseasonRankingsContent');
  if(!content) return;
  const expanded = btn.getAttribute('aria-expanded') === 'true';
  btn.setAttribute('aria-expanded', String(!expanded));
  btn.classList.toggle('collapsed', expanded);
  content.hidden = expanded;
}