fetch("/v3-test/data/owners.json")
  .then(response => response.json())
  .then(data => {
    const ownerList = document.getElementById("owner-list");

    data.owners.forEach(owner => {
      const card = document.createElement("div");

      const helmetPath = data.divisionHelmets[owner.division];

      card.innerHTML = `
        <img
          src="${helmetPath}"
          alt="${owner.division} helmet"
          width="120"
        >

        <h2>${owner.name}</h2>
        <p>${owner.division}</p>
        <p>Draft Pick #${owner.draftPick}</p>
      `;

      ownerList.appendChild(card);
    });
  })
  .catch(error => {
    console.error("Error loading owners.json:", error);
  });
