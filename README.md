# Running the Backend
To run the backend server, stay in root directory and do "uvicorn app.main:app --host 0.0.0.0 --port $PORT
"
                        AI Analytics + AI Observability Infrastructure for Teams!!
 
# How GTM Tracker Editing Works
The GTM script is local in app/routes/tracker.js
This contains all of the listening implants in the client, and how it transports that information to the /collect endpoint here.
In order for the GTM Tracker to be updated, this needs to be connected to the render server. This must be a non-local server.

This is what is in the actual GTM which reads from the /gtmtracker endpoint
```js
<script>
(function(){
  var s = document.createElement("script");
  s.src = "https://ai-analytics-7tka.onrender.com/gtmtracker.js";
  s.async = true;
  document.head.appendChild(s);
})();
</script>

Something to note for the tracker script: If you want to run the script directly into GTM you must add `<script></script>` at the beginning and end of the GTM tracker script. Right now, that isn't there.


# To Do
Reduce and organize the requests when they come into supabase (currently they just spam a bunch of requests - find out why)

## Huge Security Violation
Since we have an endpoint that is `/gtmtracker.js`, anybody can see our complete gtm tracker code. Could be a big deal down the road but we must forgoe this due to the ease of development.