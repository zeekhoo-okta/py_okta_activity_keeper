var csrftoken = getCookie('csrftoken');

var baseUrl = 'https://zeekhoo.okta.com';
var oktaSignIn = new OktaSignIn({
    baseUrl: baseUrl,
    features: {
        rememberMe: true,
        smsRecovery: true,
        multiOptionalFactorEnroll: true
    },
    labels: {
        'primaryauth.title': 'Please Sign-In',
        'help': 'Click here for more help'
    }
});

oktaSignIn.session.exists(function (exists) {
    oktaSignIn.renderEl(
        { el: '#okta-login-container' },
        function (res) {
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
});