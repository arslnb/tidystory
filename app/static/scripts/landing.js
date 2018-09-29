$(document).ready(() => {
    firebase.initializeApp(firebaseConfig);
    firebase.auth().setPersistence(firebase.auth.Auth.Persistence.NONE);
    $(".navbar-burger").click(function() {
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
    });
})

document.getElementById('searchbar').onkeypress = function(e){
    if (!e) e = window.event;
    var keyCode = e.keyCode || e.which;
    if (keyCode == '13'){
      window.location.href="/search?q=" + $('#searchbar').val()
      return false;
    }
  }

$(document).on('click', '.twitter-signin', (ev) => {
    $(ev.currentTarget).attr("disabled", "disabled").addClass("is-loading")
    $('.email-signin').attr("disabled", "disabled")
    let provider = new firebase.auth.TwitterAuthProvider();
    firebase.auth().signInWithPopup(provider).then(function(user) {
        let userData = user.user;
        return userData.getIdToken().then(idToken => {
            $.ajax({
                type: "POST",
                url: '/v1/user',
                data: JSON.stringify({
                    'grant_type': 'twitter',
                    'user': userData,
                    'id_token': idToken
                }),
                dataType: 'json',
                contentType: "application/json",
                success: () => {
                    window.location.href = "/"
                }
            });
        });
      }).catch(function(error) {
        $('.twitter-signin').removeAttr("disabled", "disabled").removeClass("is-loading")
        $('.email-signin').removeAttr("disabled", "disabled")
        var errorMessage = error.message;
        $('.error-message').text(errorMessage)
        $('.error-holder').css('display', 'flex')
    });
})

$(document).on('click', '.email-trigger', (ev) => {
    $(ev.currentTarget).attr("disabled", "disabled").addClass("is-loading")
    $('.twitter-signin').attr("disabled", "disabled")

    let email = $('.email-val').val().length >= 5 ?$('.email-val').val() : false
    let password = $('.pwd-val').val().length >= 8 ? $('.pwd-val').val() : false

    if(email && password){
        if($(ev.currentTarget).hasClass('email-signin')){
            firebase.auth().signInWithEmailAndPassword(email, password).then(user => {
                let userData = user.user;
                return userData.getIdToken().then(idToken => {
                    $.ajax({
                        type: "POST",
                        url: '/v1/user',
                        data: JSON.stringify({
                            'grant_type': 'password',
                            'user': userData,
                            'id_token': idToken
                        }),
                        dataType: 'json',
                        contentType: "application/json",
                        success: () => {
                            window.location.href = "/"
                        }
                    });
                });
            }).catch(function(error) {
                $('.twitter-signin').removeAttr("disabled", "disabled")
                $('.email-signin').removeAttr("disabled", "disabled").removeClass("is-loading")
                var errorMessage = error.message;
                $('.error-message').text(errorMessage)
                $('.error-holder').css('display', 'flex')
            });
        } else {
            firebase.auth().createUserWithEmailAndPassword(email, password).then(user => {
                let userData = user.user;
                return userData.getIdToken().then(idToken => {
                    $.ajax({
                        type: "POST",
                        url: '/v1/user',
                        data: JSON.stringify({
                            'grant_type': 'password',
                            'user': userData,
                            'id_token': idToken
                        }),
                        dataType: 'json',
                        contentType: "application/json",
                        success: () => {
                            window.location.href = "/"
                        }
                    });
                });
            }).catch(function(error) {
                $('.twitter-signin').removeAttr("disabled", "disabled")
                $('.email-signin').removeAttr("disabled", "disabled").removeClass("is-loading")
                var errorMessage = error.message;
                $('.error-message').text(errorMessage)
                $('.error-holder').css('display', 'flex')
            });
        }
    } else {
        $('.twitter-signin').removeAttr("disabled", "disabled")
        $('.email-signin').removeAttr("disabled", "disabled").removeClass("is-loading")
        var errorMessage = "Invalid email or password :(";
        $('.error-message').text(errorMessage)
        $('.error-holder').css('display', 'flex')
    }
});

$(document).on('click', '.reset-pwd', (ev) => {
    $(ev.currentTarget).attr("disabled", "disabled").addClass("is-loading")
    let email = $('.email-val').val().length >= 5 ?$('.email-val').val() : false
    if(email){
        firebase.auth().sendPasswordResetEmail(email).then(user => {
            window.location.href = "/"
        }).catch(function(error) {
            $('.reset-pwd').removeAttr("disabled", "disabled").removeClass("is-loading")
            var errorMessage = error.message;
            $('.error-message').text(errorMessage)
            $('.error-holder').css('display', 'flex')
        });
    } else {
        $('.reset-pwd').removeAttr("disabled", "disabled").removeClass("is-loading")
        var errorMessage = "Invalid email address :(";
        $('.error-message').text(errorMessage)
        $('.error-holder').css('display', 'flex')
    }
})

$('.create-story').click(() => {
    $('.create-modal').addClass('is-active');
})

$('.create-modal-close').click(() => {
  $('.error-message').text("")
  $('.error-holder').css('display', 'none')
  $('.create-modal').removeClass('is-active');
})

$('.send-story').click((ev) => {
    $(ev.currentTarget).attr("disabled", "disabled").addClass('is-loading')
    let url = $('.story-link').val().length ? $('.story-link').val() : false
    let lmk = $('.lmk-handle').val().length ? $('.lmk-handle').val() : false
    if(url && lmk){
        $.ajax({
            type: "POST",
            url: '/v1/story',
            data: JSON.stringify({
                'tweet_url': url,
                'lmk': lmk
            }),
            dataType: 'json',
            contentType: "application/json",
            success: () => {
                location.reload()
            }
        });
    } else {
        $('.send-story').removeAttr("disabled", "disabled").removeClass('is-loading')
        var errorMessage = "Obviously can't do this without a valid link or handle :("
        $('.error-message').text(errorMessage)
        $('.error-holder').css('display', 'block')
    }
})
