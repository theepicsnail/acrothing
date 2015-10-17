Request = (function () {
    // Helper for doing async http get/post
    function http_promise(setup_request) {
        return new Promise(function (resolve, reject) {
            var xhttp = new XMLHttpRequest();
            xhttp.onerror = function () {
                reject(Error('xhttp error'));
            };

            xhttp.onload = function () {
                if (xhttp.status == 200) {
                    resolve(xhttp.responseText);
                } else {
                    reject(Error(xhttp.statusText));
                }
            };

            setup_request(xhttp);
        });
    }

    // export Request.GET and Request.POST
    return {
        // POST('/some/endpoint', {key:value, key2:value2...}).then(...).catch(...)
        POST: function (url, data) {
            return http_promise(function (xhttp) {
                xhttp.open("POST", url, true);
                xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                xhttp.send(JSON.stringify(data));
            });
        },
        GET: function (url) {
            return http_promise(function (xhttp) {
                xhttp.open("GET", url, true);
                xhttp.send();
            });
        }
    };
})();