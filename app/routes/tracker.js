
(
  function () {
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

  // This will be able to grab any fetch request made by the app
  window.fetch = function () {
    var url = arguments[0];
    var options = arguments[1] || {};
    var method = options.method ? options.method : "GET";

    console.log(url, method, options);

    // Add a request ID to track requests/responses together
    var requestId = makeRequestId();
    
    // Get request body if there is one
    var requestBody = null;
    try {
      if (options.body) {
        requestBody = String(options.body).slice(0,5000) // Consolidating it to 5000 chars
      }
    } catch (e) {}

    // Track request
    try{
      navigator.sendBeacon(
        "https://ai-analytics-7tka.onrender.com/collect",
        new Blob(
          [JSON.stringify({
            project_id: "aianalyticstest",
            event_type: "user_input",
            request_id: requestId,
            payload: {
              url: url,
              method: method,
              body: requestBody,
              timestamp: Date.now()
            }
          })],
          { type: "application/json" }
        )
      );
    } catch(e) {}
    
    
    // Call the real fetch call in their app's backend   
    return originalFetch.apply(window, arguments).then(function (response) {
      /* As we call, let's grab the response to push to our backend */
      
      // Clone response so we can read its body response safely (we don't interfere with the services of the app)
      var cloned;
      var bodyText = null;
      
      // First try getting the cloned response
      try { cloned = response.clone(); } catch (e) {}
      
      // Now try reading the body text returned
      return (cloned ? cloned.text() : Promise.resolve(null)).then(function (text) {
        bodyText = text;
        
        // Send it all through
        try {
          // Track response WITH DATA
          navigator.sendBeacon(
            "https://ai-analytics-7tka.onrender.com/collect",
            new Blob(
              [JSON.stringify({
                project_id: "aianalyticstest",
                event_type: "ai_response",
                request_id: requestId,
                payload: {
                  url: url,
                  status: response.status,
                  body: bodyText ? bodyText.slice(0, 5000) : null, // limit so you don’t send huge payloads
                  timestamp: Date.now()
                }
              })],
              { type: "application/json" }
            )
          );
        } catch (e) {}

        return response;
      }).catch(function () {
        // Fallback if body cannot be read
        try {
          navigator.sendBeacon(
            "https://ai-analytics-7tka.onrender.com/collect",
            new Blob(
              [JSON.stringify({
                project_id: "aianalyticstest",
                event_type: "ai_response",
                request_id: requestId,
                payload: {
                  url: url,
                  status: response.status,
                  body: null,
                  timestamp: Date.now()
                }
              })],
              { type: "application/json" }
            )
          );
        } catch (e) {}

        return response;
      });
    });
  };
})();    
