function showTab(event, tabName){

    document.querySelectorAll(".tab-content").forEach(function(tab){
        tab.classList.remove("active");
    });

    document.querySelectorAll(".tab-btn").forEach(function(btn){
        btn.classList.remove("active");
    });

    document.getElementById(tabName).classList.add("active");

    event.currentTarget.classList.add("active");

}

function searchPDFs(){

    let filter = document.getElementById("searchBox").value.toLowerCase();

    let cards = document.querySelectorAll(".pdf-card");

    cards.forEach(function(card){

        let title = card.querySelector("h3").innerText.toLowerCase();

        if(title.includes(filter))
            card.style.display = "";
        else
            card.style.display = "none";

    });

}