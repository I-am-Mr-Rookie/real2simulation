import React from '../../Build/web/node_modules/react/index.js';
import { createRoot } from '../../Build/web/node_modules/react-dom/client.js';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { writeAgentMode } from '../../Build/web/src/workspace/live.mjs';
const { useLive, Centre, Meter } = createLive(React, () => '⋯');
writeAgentMode(localStorage, 'standard', 'n82-synthetic-owner');
function App() {
  const L = useLive(true, () => {}, 'n82-synthetic-owner');
  return React.createElement(React.Fragment, null,
    React.createElement('header', null, React.createElement('h1', null, 'N82 room deletion: local component QA'),
      React.createElement('p', null, 'Synthetic test data only. Actual workspace module, CSS and owner-scoped API. No authentication or model calls.')),
    React.createElement(Centre, { L }), React.createElement('footer', null, React.createElement(Meter, { L })));
}
createRoot(document.getElementById('root')).render(React.createElement(App));
