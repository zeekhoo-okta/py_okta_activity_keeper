var has_token_flag = document.getElementById('has_token_flag');
var xhttp = new XMLHttpRequest();

var csrftoken = getCookie('csrftoken');

function recordTask(id, action) {
    element = document.getElementById('has_token_flag');
    if (element.innerHTML == '1') {
        xhttp.open("POST", "/taskaction/" + id + "/");
        xhttp.setRequestHeader('X-CSRFToken', csrftoken);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"action": action}));
        xhttp.onreadystatechange = function() {
            var element = document.getElementById('row_' + id);
            if (element != null) {
                element.parentNode.removeChild(element);
            }
        }
    } else {
        url = "/sfdc/oauth/init/";
        window.location = url;
    }
}

function dismissTask(id) {
    console.log('dismiss task ' + id)
    xhttp.open("DELETE", "/task/" + id + "/");
    xhttp.setRequestHeader('X-CSRFToken', csrftoken);
    xhttp.send();
    xhttp.onreadystatechange = function() {
        var element = document.getElementById('row_' + id);
        if (element != null) {
            element.parentNode.removeChild(element);
        }
    }
}

function taskDetails(id) {
    var buttonsDisplay = 'hidden';
    if (document.getElementById('desc_' + id).className != 'hidden') {
        buttonsDisplay = 'col-xs-3';

        document.getElementById('desc_' + id).className = 'hidden';

    } else {
        document.getElementById('desc_' + id).className = 'x';
    }
}