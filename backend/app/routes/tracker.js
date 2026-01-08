
(
  function () {
    // Prevents loading the script multiple times
  if (window.__AI_ANALYTICS_LOADED__) return;
    window.__AI_ANALYTICS_LOADED__ = true;

  // Creates a requestId in case there is no crypto.randomUUID available
  function makeRequestId() {
    if (window.crypto && crypto.randomUUID) {
      return crypto.randomUUID();
    }

      return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
        (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
      );
    }

    // Grab the fetch to the backend
    var originalFetch = window.fetch;

  // grab the api key from the script tag
  const script = document.currentScript;
  const PUBLIC_API_KEY = script?.getAttribute("public-api-key");

  // Store valid urls here chosen by the user
  var validUrls = [];

  // Store all urls ever fetched here
  var allUrls = [];

  // Call endpoint /config to get valid and all urls for this project
  originalFetch("https://ai-analytics-7tka.onrender.com/config?public_api_key=" + encodeURIComponent(PUBLIC_API_KEY))
    .then(function (response) {
      if(!response.ok) {
        throw new Error("Network response was not ok");
      }

      return response.json();
    })
    .then(function (data) {
      validUrls = Array.isArray(data.valid_urls) ? data.valid_urls : [];
      allUrls = Array.isArray(data.all_urls) ? data.all_urls : [];
    })
    .catch(function (e) {
      console.warn("Error fetching config for AI Analytics:", e);
      // In case of error, just keep going with empty validUrls and allUrls
      allUrls = [];
      validUrls = [];
    });

  // This will be able to grab any fetch request made by the app
  window.fetch = function () {
    // url is of the form "/api/chat" from the backend server, never the full url
    var url = arguments[0];
    
    // Store all urls ever seen
    if (!allUrls.includes(url)) {
      allUrls.push(url);

      // Send the updated allUrls to the backend
      originalFetch(("https://ai-analytics-7tka.onrender.com/update_api_urls?public_api_key=" + encodeURIComponent(PUBLIC_API_KEY) + "&new_url=" + encodeURIComponent(url)),
        { method: "POST" }
      )
        .then(function (response) {
          if(!response.ok) {
            throw new Error("Network response was not ok");
          }
    
          return response.json();
      }).then(function (data) {
        // Update allUrls
        if(data && Array.isArray(data.all_urls)) {
          allUrls = data.all_urls;
        }
      }).catch(function (e) {
        console.warn("Error updating all URLs for AI Analytics:", e);
      });
    }

    // Before doing anything else, check if this url is in the list of valid urls
    if (!validUrls.includes(url)) {
      // If not, just call the original fetch and return
      return originalFetch.apply(window, arguments);
    }

    var options = arguments[1] || {};
    var method = options.method ? options.method : "GET";

    console.log(options);

    // Add a request ID to track requests/responses together
    var requestId = makeRequestId();

    // Track request
    try{
      // Send it all through
      originalFetch(
        "https://ai-analytics-7tka.onrender.com/collect?public_api_key=" + encodeURIComponent(PUBLIC_API_KEY),
        {
          method: "POST",
          credentials: "omit",
          mode: "cors",
          keepalive: true,
          body: JSON.stringify({
            event_type: "ai_request",
            request_id: requestId,
            payload: {
              url: url,
              method: method,
              body: options,
              timestamp: Date.now()
            }
          }),
          headers: { "Content-Type": "application/json" }
        }
      );
    } catch(e) {}
    
    
    // Call the real fetch call in their app's backend   
    return originalFetch.apply(window, arguments).then(function (response) {
      /* As we call, let's grab the response to push to our backend */
      
      // Clone response so we can read its body response safely (we don't interfere with the services of the app)
      var cloned;
      
      // First try getting the cloned response
      try { cloned = response.clone(); } catch (e) {}

      console.log(cloned);
      
      // Now try reading the body text returned
      return (cloned).then(function (response) {
        // Send it all through
        try {
          // Track response WITH DATA
          originalFetch(
            "https://ai-analytics-7tka.onrender.com/collect?public_api_key=" + encodeURIComponent(PUBLIC_API_KEY),
            {
              method: "POST",
              credentials: "omit",
              mode: "cors",
              keepalive: true,
              body: JSON.stringify({
                event_type: "ai_response",
                request_id: requestId,
                payload: {
                  url: url,
                  status: response.status,
                  body: response,
                  timestamp: Date.now()
                }
              }),
              headers: { "Content-Type": "application/json" }
            }
          );
        } catch (e) {}

        return response;
      }).catch(function () {
        // Fallback if body cannot be read
        try {
          // Track response WITHOUT DATA
          originalFetch(
            "https://ai-analytics-7tka.onrender.com/collect?public_api_key=" + encodeURIComponent(PUBLIC_API_KEY),
            {
              method: "POST",
              credentials: "omit",
              mode: "cors",
              keepalive: true,
              body: JSON.stringify({
                event_type: "ai_response",
                request_id: requestId,
                payload: {
                  url: url,
                  status: response.status,
                  body: null,
                  timestamp: Date.now()
                }
              }),
              headers: { "Content-Type": "application/json" }
            }
          );
        } catch (e) {}

        return response;
      });
    });
  };
})();    
