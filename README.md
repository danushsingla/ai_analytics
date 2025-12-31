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
Create a table in the frontend showing a list of websites they have
More testing must be done to ensure security of using an api key with the use of api urls selection
Create listening schema since grabbing api data can vary per call

## Huge Security Violations
Since we have an endpoint that is `/gtmtracker.js`, anybody can see our complete gtm tracker code. Could be a big deal down the road but we must forget this due to the ease of development.
RLS is disabled for all tables in Supabase, this needs to be addressed at a later time
Clerk Auth will always be in dev mode unless a domain is purchased (with valid DNS)
Since public api key is used for confirming incoming requests, multiple security issues can happen (such as spam)

# Analysis
## Semantic Analysis (how does the customer feel talking to the AI?)
## Latency Analysis (how fast the AI can respond to queries?)
Show average latency per endpont
Show average latency per minute over time graph
## Usage Rate (How much is the AI used compared to other services?)
## Human-Sounding Rate (How much does AI sound like a human? We could provide examples of real responses from the AI for management to analyze)
## Breach Analysis - Analyze cases of potential breaches in private information
## Usage/Traffic Analysis - Note how often usage in the AI changes over time (graph)
## API Usage for the AI - Analyzing the cost of the AI based on the model used

# Features for later on
Add parallel updating of latency_rollup and other tables in some shape or form
