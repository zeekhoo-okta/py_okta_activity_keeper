function getBaseUrl() {
    element = document.getElementById('okta-org');
    return element.innerHTML;
}

var baseUrl = getBaseUrl();

var oktaSignIn = new OktaSignIn({
    baseUrl: baseUrl,
});

oktaSignIn.session.get(function (res) {
    if (res.status === 'ACTIVE') {
        oktaSignIn.session.close(function (err) {
            if (err) {
                console.log(err);
                return;
            }
        });
    }
})
