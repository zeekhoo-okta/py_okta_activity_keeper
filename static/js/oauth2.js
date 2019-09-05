function urlParams() {
    var urlParams;
    (window.onpopstate = function () {
        var match,
            pl     = /\+/g,  // Regex for replacing addition symbol with a space
            search = /([^&=]+)=?([^&]*)/g,
            decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
            query  = window.location.search.substring(1);

        urlParams = {};
        while (match = search.exec(query))
           urlParams[decode(match[1])] = decode(match[2]);
    })();

    return urlParams;
}

function oauth2Callback(url, redirect) {
    var csrftoken = getCookie('csrftoken');

    var params = urlParams();
    var access_code = params['code'];

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", url);
    xhttp.setRequestHeader('X-CSRFToken', csrftoken);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({"code": access_code}));
    xhttp.onreadystatechange = function() {
        status = xhttp.status;
        if (status == 401) {
            window.location.href = '/login';
        }
        if (status == 200) {
            window.location.href = redirect;
        }
    }
}