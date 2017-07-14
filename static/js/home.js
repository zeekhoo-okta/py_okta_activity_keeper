function getBaseUrl() {
    element = document.getElementById('okta-org');
    return element.innerHTML;
}

function getClientId() {
    element = document.getElementById('client-id');
    return element.innerHTML;
}

var baseUrl = getBaseUrl();
var clientId = getClientId();
var current_Url = window.location.href;

var oktaSignIn = new OktaSignIn({
    baseUrl: baseUrl,
    clientId: clientId,
    redirectUri: current_Url + "oidc/callback/",
    authParams: {
        display: 'page',
        responseType: ['id_token'],
        responseMode: 'form_post',
        scopes: ['openid', 'profile'],
    },
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


oktaSignIn.session.get(function (res) {
  if (res.status === 'ACTIVE') {
        var authClient = new OktaAuth({
            url: baseUrl,
            clientId: clientId,
            redirectUri: current_Url + "oidc/callback/",
        });
        authClient.token.getWithRedirect({
            responseType: ['id_token'],
            responseMode: 'form_post',
            scopes: ['openid', 'profile'],
        });
  }
  else {
    console.log('no session. render the login widget');
    oktaSignIn.renderEl(
      {el: '#okta-login-container'},
      function (res) {
        console.log('status:',res.status);
        var id_token = res.id_token || res.idToken;
        console.log('token=', id_token);

        if (res.status === 'SUCCESS') {
            console.log('success!');
        }
      },
      function error(err) {
        console.log('Unexpected error authenticating user: %o', err);
      }
    );
  }
});

