function searchOpptys() {
    var searchOp = document.getElementById('searchOp');
    var xhttp = new XMLHttpRequest();

    url = "/sfdc/search/";
    q = searchOp.value;
    if (q.length >= 3) {
        url += '?q=' + q;
    }

    xhttp.open("GET", url);
    xhttp.setRequestHeader('Accept', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send();
    xhttp.onreadystatechange = function() {
        if (xhttp.status == 401) {
            window.location.href = '/sfdc/oauth/init';
        }
        if (xhttp.responseText != null && xhttp.responseText != '') {
            recents = JSON.parse(xhttp.responseText);
            opportunities = recents.opportunities;
            drawTable(opportunities);
        }
    }
}

function drawTable(tableData) {
    var i;
    var draw = "";
    for(i = 0; i < tableData.length; i++) {
        opportunity_id = '-1'
        if (tableData[i].Id != null) {
            opportunity_id = tableData[i].Id;
        }
        draw += '<tr>' +
        '<td style="display:none">' + opportunity_id + '</td>' +
        '<td style="display:none">' + tableData[i].Name + '</td>' +
        '<td>' + tableData[i].Name;

        if (tableData[i].Owner != null) {
            draw += '<br><p style="font-size:11px">' +
            'Owner:&nbsp;' + tableData[i].Owner + '&nbsp;&nbsp;Amount:&nbsp;' + tableData[i].Amount +
            '</p>' +
            '</td>' +
            '<td style="font-size:11px">' + tableData[i].Stage + '<br>' + 'Close:&nbsp;' + tableData[i].CloseDate + '</td>';
        }

        draw += '</tr>';
    }
    document.getElementById('search_results').innerHTML = draw;
    document.getElementById('selectedOp').innerHTML = '';
    document.getElementById('selectedOpId').innerHTML = '';
}


function selectOp() {
    var tbody = document.getElementById("search_results");

    tbody.onclick = function (e) {
        e = e || window.event;
        var target = e.srcElement || e.target;
        while (target && target.nodeName !== "TR") {
            target = target.parentNode;
        }
        if (target) {
            var cells = target.getElementsByTagName("td");
            var opId = cells[0].innerHTML;
            if (opId != '-1') {
                var op = cells[1].innerHTML;
                document.getElementById('selectedOp').innerHTML = '<p class="form-control-static">' + op + '</p>';
                document.getElementById('selectedOpId').innerHTML = '<p class="form-control-static">' + opId + '</p>';
                document.getElementById('opportunity_id').value = opId;

                document.getElementById('search_results').innerHTML = '';
                document.getElementById('tab_head').innerHTML = '';
            }
        }
    };
}