checkbox = document.getElementById("tick")
comps = document.getElementsByClassName("noComp")

checkbox.addEventListener("change", (change) => {
    //console.log(checkbox.checked)
    if(checkbox.checked){
        for (i=0;i<comps.length;i++){
            comps[i].style.display = "none"
        }
    }else{
        for (i=0;i<comps.length;i++){
            comps[i].style.display = ""
        }
    }
})

checkbox2 = document.getElementById("tick2")
missing = document.getElementsByClassName("missing")
completed = document.getElementsByClassName("completed")

checkbox2.addEventListener("change", (change) => {

    for (i=0;i<missing.length;i++){
        missing[i].style.display = checkbox2.checked ? "none" : ""
    }
    for (i=0;i<completed.length;i++){
        completed[i].style.display = checkbox2.checked ? "" : "none"
    }
})
