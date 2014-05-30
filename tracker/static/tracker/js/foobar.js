/**
 * Created by Nathaniel on 5/30/14.
 */

function reload_callback(json) {
    var x = 5;
    if (json.success == true) {
        location.reload();
    }
}

function check_reload() {
    Dajaxice.tracker.check_refresh(reload_callback);
}

setInterval(check_reload, 5000);

function reload_site() {
    setTimeout(function () {
        location.reload()
    }, 500);
}

function skip_song() {
    Dajaxice.tracker.skip_song(reload_site);
}