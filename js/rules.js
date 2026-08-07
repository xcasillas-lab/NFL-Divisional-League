
document.querySelectorAll('.rules-jumpbar [data-rule-target]').forEach(function(btn){
  btn.addEventListener('click', function(){
    var target = document.getElementById(btn.getAttribute('data-rule-target'));
    if(target){ target.scrollIntoView({behavior:'smooth', block:'start'}); }
  });
});
