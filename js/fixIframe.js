$(document).getElementById("content-frame").onload = function(){
        var temp = document.getElementById("content-frame").contentWindow.location.href;
        var httpIndex = temp.indexOf(".com")


        if (temp.includes("?redirected=True")){
            console.log("here");
            temp = temp.slice(0, temp.indexOf('?'));
            console.log(temp);
        }
        history.replaceState(null,null,temp);
        if (httpIndex != -1){
            if (httpIndex + 5 >= temp.length){
                location.reload();
            }
        } else{
            var localIndex = temp.indexOf(":16080")
            console.log(temp);
            console.log(localIndex);
            if (localIndex + 7 >= temp.length){
                location.reload();
            }
        }
    };