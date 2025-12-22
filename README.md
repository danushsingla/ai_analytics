# Running the Backend
To run the backend server, stay in root directory and do "uvicorn app.main:app --host 0.0.0.0 --port $PORT
"
                        AI Analytics + AI Observability Infrastructure for Teams!!
 
# GTM Tracker

## Understanding how GTM works
On Google Tag Manager (GTM), the script constantly reads from the /gtmtracker.js endpoint of this site. Any updates to the script there, which is tracker.js locally, updates the GTM immediately.

### Triggers
There are three main triggers GTM provides on default. One can chose between all three or none as desired. Note for each trigger: These are basic understandings of each trigger. They are subject to change when new information is acquired.

#### Page Initialization (Used)
Only one used because it loads initially when a page is loaded in and only loads in then. After the script loads, it thereafter searches for triggers (whenever an api call happens, can be specified in the script itself). Doing this prevents duplicate triggers (running more than once for an api call, needlessly filling data tables).

#### Consent Initialization (Not used)
Used for setting any consent defaults for a user, and updates whenever those consents change. This is not used because it can run the script more than once whenever some consents are changed, duplicating or complicating triggers unnecessarily. The issue with running this script more than once is that it can wrap onto itself, making a call happen more than once depending on the number of wraps that occurred.

#### Page View (Not used)
Like Consent Initiailization, runs the risk of running more than once after the page initially loads whenever something is viewed further in the page (such as when you are on /skills and then click on the webpage to go into /skills/python, this can run twice for both causing a double wrap).

## How GTM Tracker Editing Works
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
```

Something to note for the tracker script: If you want to run the script directly into GTM you must add `<script></script>` at the beginning and end of the GTM tracker script. Right now, that isn't there.


# To Do
Move all links in code to ENV keys
Publish test app as vercel site for proper testing (ensure Clerk is in production mode)
Track client site list links - Due to CORS issues where client apps using tools like Clerk utilize cookies, those cookies get sent to our server unintentionally which causes lots of issues with the browser. To keep security prime, we must keep track of a list of client apps and add them to that list for allow_origins
Create a decent-ish frontend with the ability to choose api urls and allowlist urls

## Huge Security Violations
Since we have an endpoint that is `/gtmtracker.js`, anybody can see our complete gtm tracker code. Could be a big deal down the road but we must forgoe this due to the ease of development.
RLS is disabled for all tables in Supabase, this needs to be addressed at a later time
Remove localhost from allowed origins for CORS