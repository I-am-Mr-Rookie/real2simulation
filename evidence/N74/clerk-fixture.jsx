import React from 'react';
export const useAuth=()=>({isLoaded:true,isSignedIn:new URLSearchParams(location.search).get('signed')==='1'});
export const UserButton=()=> <button aria-label="Fixture user menu" style={{width:28,height:28,borderRadius:'50%',padding:0,flexShrink:0}}>U</button>;
