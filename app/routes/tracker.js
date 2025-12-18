
(function () {
  // Grab the fetch to the backend
  var originalFetch = window.fetch;

  // This will be able to grab any fetch request made by the app
  window.fetch = function () {
    var url = arguments[0];
    var options = arguments[1] || {};
    var method = options.method ? options.method : "GET";
    
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
