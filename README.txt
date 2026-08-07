DFFL WEBSITE VERSION 2.1 — OPTIMIZED PRODUCTION BUILD
Source: index(20260807-181541).html

WHAT CHANGED FROM 2.0
- Home + Roster Submissions remain together in index.html.
- Other tabs remain separate HTML pages.
- CSS moved into css/style.css.
- Roster / Google Form JavaScript moved into js/roster.js.
- Countdown moved into js/countdown.js.
- Rules controls moved into js/rules.js.
- Newsletter ranking toggle moved into js/newsletter.js.
- Embedded base64 helmet graphics were extracted into assets/images/.
- Duplicate images are automatically reused instead of being embedded over and over.

WHY THIS IS BETTER
- Much smaller HTML files.
- Faster browser parsing and caching.
- Future page updates usually require replacing only one HTML file.
- Helmet images can be cached by the browser and reused across pages.
- Roster form remains connected to the same Google Form.

UPLOAD TO GITHUB
1. Unzip this package.
2. Upload ALL files and folders inside it to the ROOT of NFL-Divisional-League.
3. This includes css/, js/, assets/, the HTML files, CNAME, and README.txt.
4. Commit the changes.
5. Keep GitHub Pages set to main / (root).
6. After deployment, open https://dff-league.com and hard-refresh or use Incognito.

FILES
index.html               Home + Roster Submissions
standings.html           Standings
matchups.html            Weekly Matchups
lastweek.html            Last Week
playoffs.html            Playoffs
newsletter.html          Newsletter
schedule.html            Schedule
rules.html               Rules
css/style.css            Shared styling
js/roster.js             Roster builder + Google Form submission
js/countdown.js          Season countdown
js/rules.js              Rules-page controls
js/newsletter.js         Newsletter ranking toggle
assets/images/           Extracted DFFL helmet graphics
CNAME                    dff-league.com
