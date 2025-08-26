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