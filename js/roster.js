


function showTab(tabId, btn){
  document.querySelectorAll('.tab-section').forEach(section => {
    section.classList.remove('active');
  });
  document.querySelectorAll('.tab-btn').forEach(button => {
    button.classList.remove('active');
  });
  const selected = document.getElementById(tabId);
  if(selected){
    selected.classList.add('active');
  }
  if(btn){
    btn.classList.add('active');
  }
  window.scrollTo({top:0, behavior:'smooth'});
}

const rosterDB = {"AFC East": {"Buffalo Bills": {"QB": ["Josh Allen", "Mitchell Trubisky", "Mike White"], "RB": ["James Cook", "Ray Davis", "Ty Johnson"], "WR": ["Khalil Shakir", "Keon Coleman", "Curtis Samuel", "Joshua Palmer"], "TE": ["Dalton Kincaid", "Dawson Knox"], "DEF": ["Buffalo Bills DEF"]}, "Miami Dolphins": {"QB": ["Tua Tagovailoa", "Zach Wilson", "Quinn Ewers"], "RB": ["De'Von Achane", "Jaylen Wright", "Alexander Mattison"], "WR": ["Tyreek Hill", "Jaylen Waddle", "Nick Westbrook-Ikhine", "Malik Washington"], "TE": ["Jonnu Smith", "Julian Hill"], "DEF": ["Miami Dolphins DEF"]}, "New England Patriots": {"QB": ["Drake Maye", "Joshua Dobbs", "Joe Milton III"], "RB": ["Rhamondre Stevenson", "Antonio Gibson", "TreVeyon Henderson"], "WR": ["Stefon Diggs", "Demario Douglas", "Kayshon Boutte", "Kyle Williams"], "TE": ["Hunter Henry", "Austin Hooper"], "DEF": ["New England Patriots DEF"]}, "New York Jets": {"QB": ["Justin Fields", "Tyrod Taylor", "Adrian Martinez"], "RB": ["Breece Hall", "Braelon Allen", "Isaiah Davis"], "WR": ["Garrett Wilson", "Allen Lazard", "Josh Reynolds", "Malachi Corley"], "TE": ["Mason Taylor", "Jeremy Ruckert"], "DEF": ["New York Jets DEF"]}}, "AFC North": {"Baltimore Ravens": {"QB": ["Lamar Jackson", "Cooper Rush", "Devin Leary"], "RB": ["Derrick Henry", "Justice Hill", "Keaton Mitchell"], "WR": ["Zay Flowers", "Rashod Bateman", "DeAndre Hopkins", "Tylan Wallace"], "TE": ["Mark Andrews", "Isaiah Likely", "Charlie Kolar"], "DEF": ["Baltimore Ravens DEF"]}, "Cincinnati Bengals": {"QB": ["Joe Burrow", "Jake Browning", "Logan Woodside"], "RB": ["Chase Brown", "Zack Moss", "Samaje Perine"], "WR": ["Ja'Marr Chase", "Tee Higgins", "Andrei Iosivas", "Jermaine Burton"], "TE": ["Mike Gesicki", "Drew Sample", "Erick All Jr."], "DEF": ["Cincinnati Bengals DEF"]}, "Cleveland Browns": {"QB": ["Joe Flacco", "Kenny Pickett", "Dillon Gabriel", "Shedeur Sanders"], "RB": ["Jerome Ford", "Dylan Sampson", "Quinshon Judkins"], "WR": ["Jerry Jeudy", "Cedric Tillman", "Diontae Johnson", "Elijah Moore"], "TE": ["David Njoku", "Harold Fannin Jr."], "DEF": ["Cleveland Browns DEF"]}, "Pittsburgh Steelers": {"QB": ["Aaron Rodgers", "Mason Rudolph", "Will Howard"], "RB": ["Jaylen Warren", "Kaleb Johnson", "Kenneth Gainwell"], "WR": ["DK Metcalf", "Roman Wilson", "Calvin Austin III", "Robert Woods"], "TE": ["Pat Freiermuth", "Darnell Washington"], "DEF": ["Pittsburgh Steelers DEF"]}}, "AFC South": {"Houston Texans": {"QB": ["C.J. Stroud", "Davis Mills", "Kedon Slovis"], "RB": ["Joe Mixon", "Dameon Pierce", "Woody Marks"], "WR": ["Nico Collins", "Tank Dell", "Christian Kirk", "Jayden Higgins", "Jaylin Noel"], "TE": ["Dalton Schultz", "Cade Stover"], "DEF": ["Houston Texans DEF"]}, "Indianapolis Colts": {"QB": ["Anthony Richardson", "Daniel Jones", "Sam Ehlinger"], "RB": ["Jonathan Taylor", "Tyler Goodson", "DJ Giddens"], "WR": ["Michael Pittman Jr.", "Josh Downs", "Alec Pierce", "Adonai Mitchell"], "TE": ["Tyler Warren", "Mo Alie-Cox", "Drew Ogletree"], "DEF": ["Indianapolis Colts DEF"]}, "Jacksonville Jaguars": {"QB": ["Trevor Lawrence", "Nick Mullens", "John Wolford"], "RB": ["Travis Etienne Jr.", "Tank Bigsby", "Bhayshul Tuten"], "WR": ["Brian Thomas Jr.", "Travis Hunter", "Dyami Brown", "Parker Washington"], "TE": ["Brenton Strange", "Hunter Long"], "DEF": ["Jacksonville Jaguars DEF"]}, "Tennessee Titans": {"QB": ["Cam Ward", "Will Levis", "Brandon Allen"], "RB": ["Tony Pollard", "Tyjae Spears", "Kalel Mullings"], "WR": ["Calvin Ridley", "Treylon Burks", "Van Jefferson", "Elic Ayomanor"], "TE": ["Chig Okonkwo", "Gunnar Helm"], "DEF": ["Tennessee Titans DEF"]}}, "AFC West": {"Denver Broncos": {"QB": ["Bo Nix", "Jarrett Stidham", "Sam Ehlinger"], "RB": ["RJ Harvey", "J.K. Dobbins", "Audric Estime", "Jaleel McLaughlin"], "WR": ["Courtland Sutton", "Marvin Mims Jr.", "Troy Franklin", "Devaughn Vele"], "TE": ["Evan Engram", "Adam Trautman"], "DEF": ["Denver Broncos DEF"]}, "Kansas City Chiefs": {"QB": ["Patrick Mahomes", "Carson Wentz", "Chris Oladokun"], "RB": ["Isiah Pacheco", "Kareem Hunt", "Brashard Smith"], "WR": ["Rashee Rice", "Xavier Worthy", "Marquise Brown", "JuJu Smith-Schuster"], "TE": ["Travis Kelce", "Noah Gray"], "DEF": ["Kansas City Chiefs DEF"]}, "Las Vegas Raiders": {"QB": ["Geno Smith", "Aidan O'Connell", "Cam Miller"], "RB": ["Ashton Jeanty", "Raheem Mostert", "Zamir White"], "WR": ["Jakobi Meyers", "Tre Tucker", "Dont'e Thornton Jr."], "TE": ["Brock Bowers", "Michael Mayer"], "DEF": ["Las Vegas Raiders DEF"]}, "Los Angeles Chargers": {"QB": ["Justin Herbert", "Trey Lance", "Taylor Heinicke"], "RB": ["Omarion Hampton", "Najee Harris", "Kimani Vidal"], "WR": ["Ladd McConkey", "Quentin Johnston", "Mike Williams", "Tre Harris"], "TE": ["Will Dissly", "Tyler Conklin"], "DEF": ["Los Angeles Chargers DEF"]}}, "NFC East": {"Dallas Cowboys": {"QB": ["Dak Prescott", "Joe Milton III", "Will Grier"], "RB": ["Javonte Williams", "Jaydon Blue", "Miles Sanders"], "WR": ["CeeDee Lamb", "George Pickens", "Jalen Tolbert", "KaVontae Turpin"], "TE": ["Jake Ferguson", "Luke Schoonmaker"], "DEF": ["Dallas Cowboys DEF"]}, "New York Giants": {"QB": ["Russell Wilson", "Jameis Winston", "Jaxson Dart"], "RB": ["Tyrone Tracy Jr.", "Devin Singletary", "Cam Skattebo"], "WR": ["Malik Nabers", "Darius Slayton", "Wan'Dale Robinson", "Jalin Hyatt"], "TE": ["Theo Johnson", "Daniel Bellinger"], "DEF": ["New York Giants DEF"]}, "Philadelphia Eagles": {"QB": ["Jalen Hurts", "Tanner McKee", "Dorian Thompson-Robinson"], "RB": ["Saquon Barkley", "Will Shipley", "AJ Dillon"], "WR": ["A.J. Brown", "DeVonta Smith", "Jahan Dotson"], "TE": ["Dallas Goedert", "Grant Calcaterra"], "DEF": ["Philadelphia Eagles DEF"]}, "Washington Commanders": {"QB": ["Jayden Daniels", "Marcus Mariota", "Sam Hartman"], "RB": ["Brian Robinson Jr.", "Austin Ekeler", "Jacory Croskey-Merritt"], "WR": ["Terry McLaurin", "Deebo Samuel", "Noah Brown", "Luke McCaffrey"], "TE": ["Zach Ertz", "Ben Sinnott"], "DEF": ["Washington Commanders DEF"]}}, "NFC North": {"Chicago Bears": {"QB": ["Caleb Williams", "Tyson Bagent", "Case Keenum"], "RB": ["D'Andre Swift", "Roschon Johnson", "Kyle Monangai"], "WR": ["DJ Moore", "Rome Odunze", "Luther Burden III", "Olamide Zaccheaus"], "TE": ["Cole Kmet", "Colston Loveland"], "DEF": ["Chicago Bears DEF"]}, "Detroit Lions": {"QB": ["Jared Goff", "Hendon Hooker", "Kyle Allen"], "RB": ["Jahmyr Gibbs", "David Montgomery", "Craig Reynolds"], "WR": ["Amon-Ra St. Brown", "Jameson Williams", "Kalif Raymond", "Isaac TeSlaa"], "TE": ["Sam LaPorta", "Brock Wright"], "DEF": ["Detroit Lions DEF"]}, "Green Bay Packers": {"QB": ["Jordan Love", "Malik Willis", "Sean Clifford"], "RB": ["Josh Jacobs", "MarShawn Lloyd", "Emanuel Wilson"], "WR": ["Jayden Reed", "Romeo Doubs", "Christian Watson", "Matthew Golden"], "TE": ["Tucker Kraft", "Luke Musgrave"], "DEF": ["Green Bay Packers DEF"]}, "Minnesota Vikings": {"QB": ["J.J. McCarthy", "Sam Howell", "Brett Rypien"], "RB": ["Aaron Jones", "Jordan Mason", "Ty Chandler"], "WR": ["Justin Jefferson", "Jordan Addison", "Jalen Nailor"], "TE": ["T.J. Hockenson", "Josh Oliver"], "DEF": ["Minnesota Vikings DEF"]}}, "NFC South": {"Atlanta Falcons": {"QB": ["Michael Penix Jr.", "Kirk Cousins", "Easton Stick"], "RB": ["Bijan Robinson", "Tyler Allgeier", "Jase McClellan"], "WR": ["Drake London", "Darnell Mooney", "Ray-Ray McCloud III"], "TE": ["Kyle Pitts", "Charlie Woerner"], "DEF": ["Atlanta Falcons DEF"]}, "Carolina Panthers": {"QB": ["Bryce Young", "Andy Dalton", "Jack Plummer"], "RB": ["Chuba Hubbard", "Rico Dowdle", "Trevor Etienne"], "WR": ["Xavier Legette", "Tetairoa McMillan", "Adam Thielen", "Jalen Coker"], "TE": ["Ja'Tavion Sanders", "Tommy Tremble"], "DEF": ["Carolina Panthers DEF"]}, "New Orleans Saints": {"QB": ["Spencer Rattler", "Tyler Shough", "Jake Haener"], "RB": ["Alvin Kamara", "Kendre Miller", "Devin Neal"], "WR": ["Chris Olave", "Rashid Shaheed", "Brandin Cooks", "Bub Means"], "TE": ["Juwan Johnson", "Foster Moreau"], "DEF": ["New Orleans Saints DEF"]}, "Tampa Bay Buccaneers": {"QB": ["Baker Mayfield", "Kyle Trask", "Michael Pratt"], "RB": ["Bucky Irving", "Rachaad White", "Sean Tucker"], "WR": ["Mike Evans", "Chris Godwin", "Emeka Egbuka", "Jalen McMillan"], "TE": ["Cade Otton", "Payne Durham"], "DEF": ["Tampa Bay Buccaneers DEF"]}}, "NFC West": {"Arizona Cardinals": {"QB": ["Kyler Murray", "Jacoby Brissett", "Clayton Tune"], "RB": ["James Conner", "Trey Benson", "Emari Demercado"], "WR": ["Marvin Harrison Jr.", "Michael Wilson", "Greg Dortch"], "TE": ["Trey McBride", "Tip Reiman"], "DEF": ["Arizona Cardinals DEF"]}, "Los Angeles Rams": {"QB": ["Matthew Stafford", "Jimmy Garoppolo", "Stetson Bennett"], "RB": ["Kyren Williams", "Blake Corum", "Jarquez Hunter"], "WR": ["Puka Nacua", "Davante Adams", "Tutu Atwell"], "TE": ["Tyler Higbee", "Colby Parkinson"], "DEF": ["Los Angeles Rams DEF"]}, "San Francisco 49ers": {"QB": ["Brock Purdy", "Mac Jones", "Tanner Mordecai"], "RB": ["Christian McCaffrey", "Isaac Guerendo", "Jordan James"], "WR": ["Brandon Aiyuk", "Jauan Jennings", "Ricky Pearsall"], "TE": ["George Kittle", "Jake Tonges"], "DEF": ["San Francisco 49ers DEF"]}, "Seattle Seahawks": {"QB": ["Sam Darnold", "Drew Lock", "Jalen Milroe"], "RB": ["Kenneth Walker III", "Zach Charbonnet", "Kenny McIntosh"], "WR": ["Jaxon Smith-Njigba", "Cooper Kupp", "Marquez Valdes-Scantling", "Tory Horton"], "TE": ["Noah Fant", "AJ Barner"], "DEF": ["Seattle Seahawks DEF"]}}};
const positions = ["QB","RB","RB","WR","WR","TE","FLEX","DEF"];
const commissionerEmail = "xcasillas@gmail.com";
function init(){
  [1,2,3,4,5,6,7,8,9,10,11,12,14].forEach(w=>weekSelect.innerHTML+=`<option value="${w}">Week ${w}</option>`);
  Object.keys(rosterDB).forEach(d=>divisionSelect.innerHTML+=`<option value="${d}">${d}</option>`);
  divisionSelect.onchange=buildRosterTable; weekSelect.onchange=loadData;
  ownerName.oninput=saveDataSilent; ownerEmail.oninput=saveDataSilent;
  buildRosterTable();
}
function buildRosterTable(){
  const d=divisionSelect.value, teams=Object.keys(rosterDB[d]);
  rosterTitle.textContent=d+" Roster Submission"; availableTeams.textContent="Available teams: "+teams.join(", ");
  rosterBody.innerHTML="";
  positions.forEach((p,i)=>{
    rosterBody.innerHTML+=`<tr><td>${p}</td><td><select class="teamSel" data-row="${i}"><option value="">Select team</option>${teams.map(t=>`<option>${t}</option>`).join("")}</select></td><td><select class="playerSel" data-row="${i}"><option value="">Select player</option></select></td><td><input class="pts" data-row="${i}" type="number" step="0.1" value="0.0"></td></tr>`;
  });
  document.querySelectorAll(".teamSel").forEach(x=>x.onchange=e=>{populatePlayers(e.target.dataset.row);saveDataSilent();});
  document.querySelectorAll(".playerSel,.pts").forEach(x=>x.oninput=()=>{updateTotal();saveDataSilent();});
  loadData();
}
function populatePlayers(i){
  const d=divisionSelect.value, team=document.querySelector(`.teamSel[data-row="${i}"]`).value, pos=positions[i], ps=document.querySelector(`.playerSel[data-row="${i}"]`);
  ps.innerHTML='<option value="">Select player</option>'; if(!team)return;
  let arr = pos==="FLEX" ? [...(rosterDB[d][team].RB||[]),...(rosterDB[d][team].WR||[]),...(rosterDB[d][team].TE||[])] : (rosterDB[d][team][pos]||[]);
  arr.forEach(p=>ps.innerHTML+=`<option>${p}</option>`);
}
function key(){return "dffl_"+weekSelect.value+"_"+divisionSelect.value}
function collect(){
  let rows=[]; positions.forEach((p,i)=>rows.push({position:p,team:document.querySelector(`.teamSel[data-row="${i}"]`).value,player:document.querySelector(`.playerSel[data-row="${i}"]`).value,points:document.querySelector(`.pts[data-row="${i}"]`).value}));
  return {week:weekSelect.value,division:divisionSelect.value,owner:ownerName.value,email:ownerEmail.value,rows};
}
function saveDataSilent(){localStorage.setItem(key(),JSON.stringify(collect()));updateTotal();}
function saveData(){saveDataSilent();alert("Saved to this browser.")}
function loadData(){
  const s=localStorage.getItem(key());
  if(!s){document.querySelectorAll(".teamSel").forEach(x=>x.value="");document.querySelectorAll(".playerSel").forEach(x=>x.innerHTML='<option value="">Select player</option>');document.querySelectorAll(".pts").forEach(x=>x.value="0.0");updateTotal();return;}
  const data=JSON.parse(s); ownerName.value=data.owner||""; ownerEmail.value=data.email||"";
  data.rows.forEach((r,i)=>{document.querySelector(`.teamSel[data-row="${i}"]`).value=r.team||"";populatePlayers(i);document.querySelector(`.playerSel[data-row="${i}"]`).value=r.player||"";document.querySelector(`.pts[data-row="${i}"]`).value=r.points||"0.0";});
  updateTotal();
}
function updateTotal(){let t=0;document.querySelectorAll(".pts").forEach(x=>t+=parseFloat(x.value||0));totalScore.textContent=t.toFixed(1);}
function validateRoster(){
  const data=collect(), counts={}; Object.keys(rosterDB[data.division]).forEach(t=>counts[t]=0); let issues=[];
  data.rows.forEach(r=>{if(!r.team||!r.player)issues.push(r.position+" incomplete"); if(r.team)counts[r.team]++;});
  Object.entries(counts).forEach(([t,c])=>{if(c===0)issues.push("Missing team: "+t); if(c>3)issues.push("Too many from "+t+": "+c+" selected");});
  validationSummary.innerHTML=issues.length?`<div class="warning-box"><b>Roster issues:</b><br>${issues.join("<br>")}</div>`:`<div class="success-box">Roster is valid for a normal week with all 4 teams active.</div>`;
  return !issues.length;
}
function rosterText(){
  const d=collect();
  const weekLabel = String(d.week).startsWith("Week") ? d.week : "Week " + d.week;
  let ownerCode = (d.owner || "OWNER").toUpperCase().replace(/[^A-Z0-9]/g,"");
  let divisionCode = (d.division || "DIVISION").replace(/\s+/g,"");
  let txt=`Roster Code: 2026-W${String(d.week).replace("Week ","")}-${divisionCode}-${ownerCode}\n\nOwner: ${d.owner}\nDivision: ${d.division}\nWeek: ${weekLabel}\n\n`;
  d.rows.forEach(r=>txt+=`${r.position}: ${r.player} (${r.team})\n`);
  txt+=`\nTotal Projected/Entered Points: ${totalScore.textContent}`;
  return txt;
}
function submitByEmail(){
  saveDataSilent();validateRoster();const d=collect();if(!d.email){alert("Enter owner email first.");return;}
  location.href=`mailto:${encodeURIComponent(d.email)}?cc=${commissionerEmail}&subject=${encodeURIComponent("DFFL Week "+d.week+" Roster - "+d.division)}&body=${encodeURIComponent(rosterText())}`;
}




function submitToGoogleForm(){
  const d = collect();

  let otherSubmission = "";
  const otherBox = document.getElementById("otherSubmission");
  if(otherBox){
    otherSubmission = otherBox.value || "";
  }

  const formBase = "https://docs.google.com/forms/d/e/1FAIpQLSdo1ketMG2OewU9hnZTLhzrWpzo4Hq7SS8NBQt5eJAt1SIXKQ/viewform?usp=pp_url";

  const params = new URLSearchParams();
  params.set("entry.1141380727", d.owner || "");
  params.set("entry.175110858", d.email || "");
  params.set("entry.1651884925", "Week " + d.week);
  params.set("entry.2142922224", d.division + " Division");
  params.set("entry.1341701233", rosterText());
  params.set("entry.401323428", otherSubmission || "");
  params.set("entry.1695549654", "Yes");

  window.location.href = formBase + "&" + params.toString();
}

function exportCSV(){
  const d=collect();let csv="Week,Owner Email,Owner,Division,Position,Team,Player,Points\n";d.rows.forEach(r=>csv+=`"${d.week}","${d.email}","${d.owner}","${d.division}","${r.position}","${r.team}","${r.player}","${r.points}"\n`);
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));a.download="DFFL_Roster.csv";a.click();
}
function togglePreseasonRankings(btn){
  const content = document.getElementById('preseasonRankingsContent');
  if(!content) return;
  const expanded = btn.getAttribute('aria-expanded') === 'true';
  btn.setAttribute('aria-expanded', String(!expanded));
  btn.classList.toggle('collapsed', expanded);
  content.hidden = expanded;
}

init();
