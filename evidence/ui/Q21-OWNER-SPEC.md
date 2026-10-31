# Q21 owner UI spec (Oct31, Koushik, chat) - workspace layout + interview

Status: owner-approved direction. Supersedes the R1-R3 default for the private workspace shell and interview. Borrow layout/hierarchy/interaction only, never assets. Mobbin reference images are local only (gitignored): .tmp-mobbin-onboarding/ (O1..O6, P1..P4 *.webp).

## Picks
- O1 Perplexity onboarding: question on one side, live preview on the other (for us: the clip frame/scene next to the question) - https://mobbin.com/screens/6285fdec-d5dc-4a1e-9e16-30d8e00afa6a
- O2 Emergent: agent asks its questions in the work context ("Question 2 of 4", skip / let the agent answer, "Something else") - https://mobbin.com/screens/2c8a196a-de8f-403c-a06a-5cb746cf7e9a
- Third view (owner's own idea): project in the main/center area; the AI agent asks clarifying questions back in a RIGHT sidebar when a requested change is vague. Layout like P2 Snowflake CoCo (https://mobbin.com/flows/207dbf3f-7979-486c-94c6-76858105963b) but NOT its plain styling ("the entire design is kind of simplistic, do not take all of it"). Useful pieces: P4 Perplexity Computer question card (1/3, numbered options, Other, Continue) https://mobbin.com/screens/501351fa-f2ca-490a-93db-3bbda5d591a1 ; P1 Replit "agent needs your feedback" / "waiting for your response" state https://mobbin.com/flows/d3355324-0ea5-45af-aeda-ffe4d42a3692 ; P3 Magnific right-sidebar agent https://mobbin.com/flows/e133d0ea-5c3c-40b6-93ea-383340a1ed2a

## Shell requirements (owner, verbatim intent; modelled on the Codex desktop app he showed)
1. LEFT sidebar is collapsible/expandable by the user like modern IDEs, so it never wastes main-project space. Collapsed = only an icon rail stays at the left; icons open their panel/flyout (Codex: Home, Space, History, Customize, More... rail with flyout panels).
2. The project (scene viewport + stage content) owns the main/center area.
3. The RIGHTMOST button in the top-right header (not a window control) toggles a RIGHT panel that invokes the agent and a tool launcher, like Codex's right panel: Tools list (Side chat / agent, Files, Changes, Terminal-like log, New page, history) each with a keyboard shortcut, plus Suggested items. For Real2Sim map these to real features only, e.g. Agent (interview / clarifying questions), Clips (files), Runs & changes (job history / diff of specs), Report, History. No fake tools: a tool without a backend is omitted, not mocked.
4. The agent's clarifying questions appear in that right panel as a question card (n/N, options, free text "Other", Continue, Skip), and the center view shows a non-blocking "agent needs your answer" state.
5. Keyboard: toggles have shortcuts and visible focus; panels are aria-labelled regions; 375px: rails become overlays/drawers, no horizontal scroll.

Owner screenshots of the Codex app (local, not committed): %TEMP%/codex-clipboard-{08549aeb,5194a10a,d8a8a028,1c4abb49,861396cb,bf47c935,e4ef221e,44777a45}-*.png

## Left rail behaviour (owner addendum, Oct31 ~13:00 Dhaka; Codex desktop app screenshots cab8720c/06d71f3f)
Owner, verbatim intent: "The toggle sidebar button explicitly toggles the currently opened panel. Clicking on the icon of the panel does the same too, but the toggle sidebar button is kind of universal ... hovering the mouse over other icons ... temporarily opens. Once the mouse hovering moves to other place without clicking, the temporary view is closed. But if the mouse cursor makes a click, then that pane is opened. And the same goes for others also."
6. Activity-bar model (like VS Code / Codex): the icon rail is ALWAYS visible; each rail icon owns one pane (real content only, e.g. Navigate, This project outline, Clips, Runs & history). Exactly one pane is the "current" pane.
   - Toggle sidebar button (+ shortcut) shows/hides the CURRENT pane; the rail stays. Collapsed = icons only.
   - Click an icon: if its pane is current and open -> close it; otherwise make it current and open it (pinned).
   - Hover an icon whose pane is not open-and-current: after a short intent delay (~150 ms) its pane opens TEMPORARILY as an overlay (does not push the centre). Moving the pointer away from both the icon and the pane closes it after a short grace (~250 ms); moving into the pane keeps it open. Clicking the icon (or inside the pane's pin action) while previewing makes it the current pinned pane.
   - Keyboard/touch have no hover: focus + Enter/Space = click; Escape closes a temporary pane; touch tap = click. Temporary panes are aria-labelled, do not steal focus, and respect prefers-reduced-motion.
   - Current pane + open/closed state persist (localStorage); 375px: panes are drawers, no hover preview, no horizontal scroll.

