import React from 'react';
import {createRoot} from 'react-dom/client';
import SiteFrame from '../../Build/web/src/app/SiteFrame.jsx';
import AgentPanel from '../../Build/web/src/lab-editor/AgentPanel.jsx';
import {createLive} from '../../Build/web/src/workspace/live-view.mjs';
import {createUseVoice} from '../../Build/web/src/workspace/voice.mjs';
import {icon} from '../../Build/web/src/shell/icons.mjs';
let deny;
Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:()=>new Promise((_,reject)=>{deny=reject;})}});
const useVoice=createUseVoice(React), Live=createLive(React,icon);
function App(){
 const {voice,toggleVoice}=useVoice(()=>{});
 const L={mode:'standard',files:{items:[],loaded:true},jobs:null,voice,toggleVoice,draft:'',msgs:[],tracked:{},gpu:{tone:'red',label:'GPU sleeping',detail:''}};
 if(new URLSearchParams(location.search).has('header')) return <SiteFrame authAvailable><p>Synthetic account header fixture.</p></SiteFrame>;
 return <SiteFrame authAvailable><p>SYNTHETIC UI fixture: real components, no Clerk session or microphone access.</p>
 <button onClick={()=>deny?.(new Error('denied'))}>Deny fixture microphone</button>
 <AgentPanel scene={{objects:[]}} onScene={()=>{}} load={false}/>
 <div className="ws"><Live.Centre L={L}/><Live.Chat L={L}/></div></SiteFrame>;
}
createRoot(document.getElementById('root')).render(<App/>);
