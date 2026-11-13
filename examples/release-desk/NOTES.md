# Release desk

A build-and-deploy desk for a small web shop, designed around the protocol first.
Open `index.html` in a browser. Everything runs in the page; nothing is sent anywhere.

## How it's put together

`index.html` has four parts, in this order:

1. **The protocol engine.** The tree, `observe` with folding, views and `since`, `page`,
   `find`, `listen`, submissions with receipts, busy markers and pings, alerts with
   `confirm` and `cancel`, versions. It knows nothing about builds or deploys.
2. **The release desk.** The tree's starting data, and one handler per action: `build`,
   `deploy` and `set`. A handler checks its arguments and returns either an error, the
   changes to make at once, or the paths that go busy plus the work to do (and, for
   production, an alert to answer first).
3. **The UI.** A client of the engine, like the agent. It observes `/` with `/` expanded,
   listens on `/`, and draws whatever comes back. Every button sends a protocol call.
   Approving a production deploy is a `confirm` sent by the UI, which counts as a person.
4. **The agent console.** Every message the agent client sends and receives, with sizes
   and a running total. You can type calls as the agent, or run the sample task.

Two things happen from outside, as they would for a real app: **Push a commit**
(a developer pushing to the repository) and **Simulate CI outage** (the build runner
going offline: an app-wide alert that makes everything busy for 10 seconds).

For anything driving the page from outside, such as a browser-automation agent or a test,
`window.releaseDesk.call(msg)` sends a call as the agent and logs it in the console.

## What to try

- **Run sample task.** A scripted agent ships the latest storefront commit: it builds,
  watches the build's progress, deploys to staging, then asks to deploy to production.
  That needs a person: approve or reject it in the alert at the top of the page, and the
  agent reports back.
- **Push a commit** on storefront twice, then build. The second commit (`WIP: new search
  box`) fails its tests. Try deploying it.
- Start a build and press **Cancel**, or send the `cancel` call from its busy marker.
- **Simulate CI outage**, then try anything.
- In the console, try `{"action":"deploy","path":"/services/storefront/builds/b1","env":"production"}`
  (refused: not on staging), or `{"action":"confirm","path":"/","submission":"<id>"}` on a
  production deploy (refused: only a person may answer it).

## What building it this way showed

**The UI needed nothing the protocol doesn't offer.** It's drawn entirely from
`observe`, kept fresh by `listen`, and acts only through submissions, `confirm` and
`cancel`. The one thing it does outside the protocol is poll while something is busy,
because progress and alert countdowns deliberately send no pings.

**Two spec additions,** both now in the repo's `README.md`:

- **New nodes are born busy.** A build doesn't exist until it's finished, but the agent
  needs its id at once to watch it. So the new node appears immediately, busy, with no
  `last`, its marker naming the submission; the agent finds it by observing the builds.
- **`cancel` stops running work,** not just answers alerts. A busy marker offers the
  `cancel` call when the work can be stopped. A cancelled build is kept, with status
  `cancelled`, so the history stays complete.

**`answer_by: person` does real work here.** The agent can request a production deploy
but can't approve it: its `confirm` is refused with `not_yours`, and the alert waits for
a person. The deploy record notes both: `"by": "agent, approved by person"`.

**The numbers.** `observe /` is 1.7 KB, so nothing folds. The whole sample task, from
first look to production, is about 20 messages and 3 KB, roughly 1,100 tokens by the
console's estimate of 3 bytes per token.

## Left out on purpose

Commits other than each service's latest, logs of a build's output, rollbacks (deploy an
older build instead), and more than two environments.
