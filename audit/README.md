# Release audit

The production release is not complete until this audit is run against the deployed GitHub Pages site and Worker.

For every platform in `fixtures.json`:

1. Independently confirm the known-taken fixture at the platform's source.
2. Generate a unique candidate for the available fixture and independently confirm absence immediately before the check. A random-looking name alone is not ground truth.
3. Run both fixtures through the live site's UI and record the displayed status and detail.
4. Run the same fixtures through the CLI and record status and detail.
5. Compare source truth, site, and CLI. A platform-side block or ambiguity may result in `unknown`, but the report must name the evidence and reason. A false `available` is a release blocker.
6. Submit the production waitlist form and confirm the submission appears in Formspree.
7. On production, inspect the browser console and network errors, then visually inspect screenshots at desktop and phone viewport sizes.

The completion report table columns are: platform, taken fixture, source truth, site result, CLI result, available fixture, source truth, site result, CLI result, agreement, verdict/limitation.
