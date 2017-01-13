var csrftoken = getCookie('csrftoken');

function getBaseUrl() {
    element = document.getElementById('okta-org');
    return element.innerHTML;
}

var baseUrl = getBaseUrl();
var oktaSignIn = new OktaSignIn({
    baseUrl: baseUrl,
    features: {
        rememberMe: true,
        smsRecovery: true,
        multiOptionalFactorEnroll: true
    },
    helpLinks: {
        'custom': [{
            'text': 'No Account? Click here to Register',
            'href': '/register'
        }]
    },
    labels: {
        'primaryauth.title': 'Please Sign-In',
        'help': 'Click here for more help'
    },
});

oktaSignIn.renderEl(
    { el: '#okta-login-container' },
    function (res) {
        console.log(res);
        if (res.status === 'SUCCESS') {
            $.ajaxSetup({
                headers: { "X-CSRFToken": getCookie("csrftoken") }
            });
            $.post("/login/", JSON.stringify(res.user), function(data) {
                window.location.href="/task/";
            });
        }
    },
    function (err) {
        console.log('Unexpected error authenticating user: %o', err);
    }
);
