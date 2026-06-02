try {
    $(document).ready(function() {
        $('body').on("click change submit", "#gdpr-modal-content input[type='checkbox']", function(e) {
            var dataid = e.target.dataset.id;
            if (e.target.checked) {
                $("#gdpr-modal-content input[type='submit']." + dataid).removeClass('disabled');
                $("#gdpr-modal-content input[type='submit']." + dataid).attr('disabled', false);
            } else {
                $("#gdpr-modal-content input[type='submit']." + dataid).addClass('disabled');
                $("#gdpr-modal-content input[type='submit']." + dataid).attr('disabled', true);
            }
        });
        // signup
        $('body').on("click", "#signup-start-now", function(e) {
            $("#gdpr-modal-content input[type='submit']").addClass('disabled');
            $("#gdpr-modal-content input[type='submit']").attr('disabled', true);
            $("#gdpr-modal-content input[type='checkbox']").prop('checked', false);
            if ($(this).parents().is('#modal-signup-form')) {
                $("#gdpr-modal-content input[type='submit']").addClass('modal-signup-form-submit').removeClass('.signup-form-submit');
                $("#gdpr-modal-content input[type='checkbox']").attr('data-id', 'modal-signup-form-submit');
                $("#gdpr-modal-content input[type='submit']").removeClass('signup-form-submit');
            } else {
                $("#gdpr-modal-content input[type='submit']").addClass('signup-form-submit').removeClass('modal-signup-form-submit');
                $("#gdpr-modal-content input[type='checkbox']").attr('data-id', 'signup-form-submit');
            }
            $("#gdpr-modal-content input[type='submit']").removeClass('fb-form-submit g-form-submit githib-form-submit');
        });
        // google
        $("#social-login-button-g").hide();
        $('body').on("click", ".social-login-button-g.show-modal", function(e) {
            $("#gdpr-modal-content input[type='submit']").addClass('g-form-submit');
            $("#gdpr-modal-content input[type='checkbox']").attr('data-id', 'g-form-submit');
            $("#gdpr-modal-content input[type='submit']").removeClass('signup-form-submit fb-form-submit githib-form-submit modal-signup-form-submit');
        });
        // fb
        $("#social-login-button-fb").hide();
        $('body').on("click", ".social-login-button-fb.show-modal", function(e) {
            $("#gdpr-modal-content input[type='submit']").addClass('fb-form-submit');
            $("#gdpr-modal-content input[type='checkbox']").attr('data-id', 'fb-form-submit');
            $("#gdpr-modal-content input[type='submit']").removeClass('signup-form-submit g-form-submit githib-form-submit modal-signup-form-submit');
        });
        // github
        $("#social-login-button-github").hide();
        $('body').on("click", ".social-login-button-github.show-modal", function(e) {
            $("#gdpr-modal-content input[type='submit']").addClass('githib-form-submit');
            $("#gdpr-modal-content input[type='checkbox']").attr('data-id', 'githib-form-submit');
            $("#gdpr-modal-content input[type='submit']").removeClass('signup-form-submit g-form-submit fb-form-submit modal-signup-form-submit');
        });
        // click on gdpr submit
        $('body').on("click change submit", "#gdpr-modal-content input[type='submit']", function() {
            if (!$(this).hasClass('disabled')) {
                if ($(this).hasClass('modal-signup-form-submit')) {
                    $("#modal-signup-form").submit();
                    $('.gdpr-modal-content').hide();
                    $('#login-modal > .modal-header').show();
                    $('#login-modal > .modal-content').show();
                    $('#login-modal #signup-start-now').text('Starting');
                    $('#login-modal #signup-start-now').addClass('disabled');
                } else {
                    $('.modalCloseImg.simplemodal-close').click();
                    if ($(this).hasClass('signup-form-submit')) {
                        $('#track-signup').submit();
                        $('#signup-start-now').text('Starting');
                        $('#gdpr-modal').css('visibility', 'visible');
                        $('#signup-start-now.track-profile-email-signup').text('Creating');
                        $('#signup-start-now').addClass('disabled');
                    }
                    if ($(this).hasClass('fb-form-submit')) {
                        $("#social-login-button-fb").click();
                    }
                    if ($(this).hasClass('g-form-submit')) {
                        $("#social-login-button-g").click();
                    }
                    if ($(this).hasClass('githib-form-submit')) {
                        $("#social-login-button-github").click();
                    }
                }
            }
        });
        // modal signup
        function formValid(form_id) {
            var valid = true;
            $.each($("#" + form_id + " input[required]"), function(index, value) {
                if (!$(value).val()) {
                    valid = false;
                }
            });
            return valid;
        }
        $("body").on("click", "#signup-start-now", function() {
            var isOpenedinModal = $(this).parents().is(".modal-window");
            var form_valid = formValid('modal-signup-form');
            if (isOpenedinModal && form_valid) {
                $('#login-modal > .modal-header').hide();
                $('#login-modal > .modal-content').hide();
                $('.gdpr-modal-content').show();
                $('#gdpr-modal').css('visibility', 'hidden');
            }
        });
        // modal social
        $("body").on("click", ".social-login-button.show-modal", function() {
            var isOpenedinModal = $(this).parents().is(".modal-window");
            if (isOpenedinModal) {
                $('#login-modal > .modal-header').hide();
                $('#login-modal > .modal-content').hide();
                $('.gdpr-modal-content').show();
                $('#gdpr-modal').css('visibility', 'hidden');
            }
        });
    
        function updateSignupbtn(form_id, valid) {
            if (valid) {
                $("#" + form_id + " #signup-start-now").addClass("show-modal");
                $("#" + form_id + " #signup-start-now").removeClass("disabled");
            } else {
                $("#" + form_id + " #signup-start-now").removeClass("show-modal");
                $("#" + form_id + " #signup-start-now").addClass("disabled");
            }
        }
    
        $("body").on("change focus keyup click", "#login-modal #modal-signup-form input[required]", function() {
            var form_valid = formValid('modal-signup-form');
            updateSignupbtn("modal-signup-form", form_valid);
        });
        $("body").on("change focus keyup click", "#track-signup input[required]", function() {
            var form_valid = formValid('track-signup');
            updateSignupbtn("track-signup", form_valid);
        });
    });
} catch(exception) {
    console.error(exception)
}