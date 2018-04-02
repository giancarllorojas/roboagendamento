var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "xTYPEx",
        host: "xHOSTx",
        port: parseInt("xPORTx")
      },
      bypassList: ["xDOMAINx"]
    }
  };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
return {
    authCredentials: {
        username: "xUSERx",
        password: "xPSWDx"
    }
};
}

chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);
