(window["webpackJsonpcrypto-react"]=window["webpackJsonpcrypto-react"]||[]).push([[0],{102:function(e,a,t){},136:function(e,a,t){},137:function(e,a,t){"use strict";t.r(a);var n=t(0),r=t.n(n),c=t(8),l=t.n(c),o=t(14),i=t(12),s=t(15),u=t(16),d=t(17),m=(t(102),t(47)),p=t(10),h=t(146),b=t(179),f=t(38),g=t(3),E=t(84),O=t(29),j=t.n(O),v=t(175),y=t(139),x=t(13),k=t(30),w=t(53),S=t(24);var C={postRequest:function(e,a,t){console.log("Node ENV"),console.log(Object({NODE_ENV:"production",PUBLIC_URL:""}))},getRequest:function(e,a,t){}};function B(e,a){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);a&&(n=n.filter(function(a){return Object.getOwnPropertyDescriptor(e,a).enumerable})),t.push.apply(t,n)}return t}var T=Object(y.a)(function(e){return{root:{flexGrow:1,height:250,minWidth:290},input:{display:"flex",padding:0,height:"auto"},valueContainer:{display:"flex",flexWrap:"wrap",flex:1,alignItems:"center",overflow:"hidden"},chip:{margin:e.spacing(.5,.25)},chipFocused:{backgroundColor:Object(x.b)("light"===e.palette.type?e.palette.grey[300]:e.palette.grey[700],.08)},noOptionsMessage:{padding:e.spacing(1,2)},singleValue:{fontSize:16},placeholder:{position:"absolute",left:2,bottom:6,fontSize:16},paper:{position:"absolute",zIndex:1,marginTop:e.spacing(1),left:0,right:0},divider:{height:e.spacing(2)}}});var N=function(e){var a=e.match.params.marketname,t=Object(k.a)(),c=T(),l={input:function(e){return function(e){for(var a=1;a<arguments.length;a++){var t=null!=arguments[a]?arguments[a]:{};a%2?B(t,!0).forEach(function(a){Object(g.a)(e,a,t[a])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):B(t).forEach(function(a){Object.defineProperty(e,a,Object.getOwnPropertyDescriptor(t,a))})}return e}({},e,{color:t.palette.text.primary,"& input":{font:"inherit"}})}},o=Object(n.useState)(!0),i=Object(p.a)(o,2),s=i[0],u=i[1],d=Object(n.useState)("BTCUSDT"),m=Object(p.a)(d,2),h=m[0],b=m[1],f=Object(n.useState)([]),O=Object(p.a)(f,2),y=O[0],x=O[1],w=Object(n.useState)({}),N=Object(p.a)(w,2),M=N[0],D=N[1];function F(e){b(e),j.a.post("http://localhost:5000/api/coinpairsummary/",{coinpair:e.value}).then(function(e){D({data:e.data.coinpairdata,headers:e.data.coinpairheaders})})}console.log("The market is "+a),Object(n.useEffect)(function(){u(!0),j.a.get("http://localhost:5000/api/getavailcoinpairs/").then(function(e){var a=e.data.results.map(function(e){return{value:e,label:e}});x(a),console.log(e.data.results),u(!1)})},[]);return r.a.createElement("div",null,r.a.createElement("div",null,s?r.a.createElement(v.a,null):r.a.createElement(E.a,{classes:c,styles:l,inputId:"react-select-single",TextFieldProps:{label:"Country",InputLabelProps:{htmlFor:"react-select-single",shrink:!0}},placeholder:"Search a country (start with a)",options:y,value:h,onChange:F})),r.a.createElement("div",null,(C.postRequest(1,2,3),r.a.createElement(S.a,{data:M,header:h.value}))))},M=Object(y.a)(function(e){return{root:{width:"20%",marginTop:e.spacing(3),marginBottom:e.spacing(2)},progress:{margin:e.spacing(2)},tablerow:{display:"flex",flexDirection:"row",justifyContent:"space-evenly"},table:{minWidth:650,padding:"10px"}}}),D=r.a.lazy(function(){return t.e(3).then(t.bind(null,189))}),F=function(e){var a=M(),t=Object(n.useState)(0),c=Object(p.a)(t,2),l=(c[0],c[1],Object(n.useState)("Binance")),o=Object(p.a)(l,2),i=o[0],s=o[1],u=Object(n.useState)([]),d=Object(p.a)(u,2),m=(d[0],d[1]),h=Object(n.useState)([]),b=Object(p.a)(h,2),f=b[0],g=(b[1],Object(n.useState)([])),E=Object(p.a)(g,2),O=E[0],y=(E[1],Object(n.useState)([])),x=Object(p.a)(y,2),k=x[0],w=(x[1],Object(n.useState)([])),S=Object(p.a)(w,2),C=S[0],B=(S[1],Object(n.useState)([])),T=Object(p.a)(B,2),N=T[0],F=(T[1],Object(n.useState)([])),P=Object(p.a)(F,2),z=P[0],I=(P[1],Object(n.useState)([])),R=Object(p.a)(I,2),L=R[0];R[1],Object(n.useRef)({});return Object(n.useEffect)(function(){var a=e.match.params.exchangename;s(a),console.log("Route params has changed! "+a),j.a.post("/api/technicalssummary/",{exchange:a}).then(function(e){var a={};a.headers=e.data.topgainersheaders,a.data=e.data.topgainers,f.headers=e.data.toplosersheaders,f.data=e.data.toplosers,O.headers=e.data.unusualvolumeheaders,O.data=e.data.unusualvolume,k.headers=e.data.overboughtheaders,k.data=e.data.overbought,C.headers=e.data.oversoldheaders,C.data=e.data.oversold,N.headers=e.data.macdheaders,N.data=e.data.macd,L.headers=e.data.bullishmaheaders,L.data=e.data.bullishma,z.headers=e.data.bearishmaheaders,z.data=e.data.bearishma,m(a)})},[e.match.params]),Object(n.useEffect)(function(){},[]),r.a.createElement("div",null,r.a.createElement(n.Suspense,{fallback:r.a.createElement(v.a,{className:a.progress})},r.a.createElement(D,{exchange:i})))},P=t(176),z=t(182),I=t(186),R=t(178),L=t(59),H=t.n(L),A=t(180),U=t(143),W=t(183),G=t(184),K=t(60),V=t.n(K),Y=t(82),q=t.n(Y),J=t(181),_=t(187),X=t(177),Q=t(83),Z=t.n(Q),$=t(80),ee=t.n($),ae=Object(y.a)(function(e){return{root:{width:"20%",marginTop:e.spacing(3),marginBottom:e.spacing(2)},tablerow:{display:"flex",flexDirection:"row",justifyContent:"space-evenly"},table:{minWidth:650,padding:"10px"}}});var te=Object(f.e)(function(e){var a=ae(),t=Object(n.useState)([]),c=Object(p.a)(t,2),l=c[0],o=c[1],i=Object(n.useState)([]),s=Object(p.a)(i,2),u=s[0],d=(s[1],Object(n.useState)([])),m=Object(p.a)(d,2),h=m[0],b=(m[1],Object(n.useState)([])),f=Object(p.a)(b,2),g=f[0],E=(f[1],Object(n.useState)([])),O=Object(p.a)(E,2),v=O[0],y=(O[1],Object(n.useState)([])),x=Object(p.a)(y,2),k=x[0],w=(x[1],Object(n.useState)([])),C=Object(p.a)(w,2),B=C[0],T=(C[1],Object(n.useState)([])),N=Object(p.a)(T,2),M=N[0];return N[1],Object(n.useEffect)(function(){j.a.post("/api/frontpage/",{}).then(function(e){var a={};a.headers=e.data.topgainersheaders,a.data=e.data.topgainers,u.headers=e.data.toplosersheaders,u.data=e.data.toplosers,h.headers=e.data.unusualvolumeheaders,h.data=e.data.unusualvolume,g.headers=e.data.overboughtheaders,g.data=e.data.overbought,v.headers=e.data.oversoldheaders,v.data=e.data.oversold,k.headers=e.data.macdheaders,k.data=e.data.macd,M.headers=e.data.bullishmaheaders,M.data=e.data.bullishma,B.headers=e.data.bearishmaheaders,B.data=e.data.bearishma,o(a)})},[]),r.a.createElement("div",null,r.a.createElement(ee.a,{format:"DD-MMM-YYYY HH:mm:ss",ticking:!0,interval:1e3,timezone:"UTC"}),r.a.createElement("div",{className:a.tablerow},r.a.createElement(S.a,{data:l,header:"Top Gainers"}),r.a.createElement(S.a,{data:u,header:"Top Losers"}),r.a.createElement(S.a,{data:h,header:"Unusual Volume"})),r.a.createElement("div",{className:a.tablerow},r.a.createElement(S.a,{data:g,header:"Overbought"}),r.a.createElement(S.a,{data:v,header:"Oversold"}),r.a.createElement(S.a,{data:k,header:"MACD Indicator"})),r.a.createElement("div",{className:a.tablerow},r.a.createElement(S.a,{data:M,header:"Bullish MA"}),r.a.createElement(S.a,{data:B,header:"Bearish MA"})))}),ne=Object(y.a)({root:{background:"linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",borderRadius:3,border:0,color:"white",height:48,padding:"0 30px",boxShadow:"0 3px 5px 2px rgba(255, 105, 135, .3)"},label:{textTransform:"capitalize",color:"white",paddingLeft:"10px"}});var re=Object(f.e)(Object(h.a)({root:{background:"linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",border:0,borderRadius:3,boxShadow:"0 3px 5px 2px rgba(255, 105, 135, .3)",color:"white",height:48,padding:"0 30px"}})(function(e){var a=e.classes,t=r.a.useState(!1),c=Object(p.a)(t,2),l=c[0],o=c[1],i=r.a.useState(null),s=Object(p.a)(i,2),u=s[0],d=s[1],m=r.a.useState(null),h=Object(p.a)(m,2),g=h[0],E=h[1],O=ne();function j(a){E(null),e.history.push("/exchange/"+a)}return Object(n.useEffect)(function(){},[]),r.a.createElement("div",null,r.a.createElement(P.a,{position:"static"},r.a.createElement(X.a,null,r.a.createElement(R.a,{color:"inherit","aria-label":"Open drawer",edge:"start",onClick:function(){o(!0)},className:a.menuButton},r.a.createElement(q.a,null)),r.a.createElement(w.a,null,"Coinelytics"),r.a.createElement(b.a,{classes:{label:O.label},onClick:function(e){E(e.currentTarget)}},"Exchanges"),r.a.createElement(_.a,{id:"exchange-menu",anchorEl:g,keepMounted:!0,open:Boolean(g),onClose:function(){E(null)}},r.a.createElement(J.a,{onClick:function(){return j("Binance")}},"Binance"),r.a.createElement(J.a,{onClick:function(){return j("BitTrex")}},"BitTrex"),r.a.createElement(J.a,{onClick:function(){return j("Bitfinex")}},"Bitfinex"),r.a.createElement(J.a,{onClick:function(){return j("DigiFinex")}},"DigiFinex"),r.a.createElement(J.a,{onClick:function(){return j("HitBTC")}},"HitBTC"),r.a.createElement(J.a,{onClick:function(){return j("HuobiGlobal")}},"Huobi Global"),r.a.createElement(J.a,{onClick:function(){return j("Kucoin")}},"Kucoin"),r.a.createElement(J.a,{onClick:function(){return j("OKEx")}},"OKEx")),r.a.createElement(b.a,{classes:{label:O.label},onClick:function(e){d(e.currentTarget)}},"Markets"),r.a.createElement(_.a,{id:"market-menu",anchorEl:u,keepMounted:!0,open:Boolean(u),onClose:function(){d(null)}},r.a.createElement(J.a,{onClick:function(){console.log("click handler"),d(null),e.history.push("/market/btcusdt")}},"BTC/USDT")))),r.a.createElement(I.a,{className:a.drawer,variant:"persistent",anchor:"left",open:l,classes:{paper:a.drawerPaper}},r.a.createElement("div",{className:a.drawerHeader},r.a.createElement(R.a,{onClick:function(){o(!1)}},r.a.createElement(Z.a,null))),r.a.createElement(z.a,null),r.a.createElement(A.a,null,["Inbox","Starred","Send email","Drafts"].map(function(e,a){return r.a.createElement(U.a,{button:!0,key:e},r.a.createElement(W.a,null,a%2===0?r.a.createElement(H.a,null):r.a.createElement(V.a,null)),r.a.createElement(G.a,{primary:e}))})),r.a.createElement(z.a,null),r.a.createElement(A.a,null,["All mail","Trash","Spam"].map(function(e,a){return r.a.createElement(U.a,{button:!0,key:e},r.a.createElement(W.a,null,a%2===0?r.a.createElement(H.a,null):r.a.createElement(V.a,null)),r.a.createElement(G.a,{primary:e}))}))),r.a.createElement(f.a,{exact:!0,path:"/",component:te}),r.a.createElement(f.a,{path:"/market/:marketname",component:N}),r.a.createElement(f.a,{path:"/exchange/:exchangename",component:F}))}));t(140),t(142),t(86),t(141),t(85),t(87),Object(y.a)(function(e){return{root:{width:"40%",marginTop:e.spacing(3),overflowX:"auto"},table:{minWidth:650}}});function ce(e,a,t,n,r){return{name:e,calories:a,fat:t,carbs:n,protein:r}}ce("Frozen yoghurt",159,6,24,4),ce("Ice cream sandwich",237,9,37,4.3),ce("Eclair",262,16,24,6),ce("Cupcake",305,3.7,67,4.3),ce("Gingerbread",356,16,49,3.9);var le=function(e){function a(){var e,t;Object(o.a)(this,a);for(var n=arguments.length,r=new Array(n),c=0;c<n;c++)r[c]=arguments[c];return(t=Object(s.a)(this,(e=Object(u.a)(a)).call.apply(e,[this].concat(r)))).state={isMobile:!1},t}return Object(d.a)(a,e),Object(i.a)(a,[{key:"componentDidMount",value:function(){window.addEventListener("resize",this.resize.bind(this)),this.resize()}},{key:"resize",value:function(){this.setState({isMobile:window.innerWidth<=760})}},{key:"displayMobile",value:function(){return this.state.isMobile?r.a.createElement("div",null,"This is Mobile"):r.a.createElement("div",null,"This is NOT MOBILE")}},{key:"render",value:function(){return r.a.createElement(m.a,null,r.a.createElement("div",{className:"App"},r.a.createElement(re,null)))}}]),a}(n.Component);t(136);l.a.render(r.a.createElement(le,null),document.getElementById("root"))},24:function(e,a,t){"use strict";var n=t(0),r=t.n(n),c=t(139),l=t(140),o=t(142),i=t(86),s=t(141),u=t(85),d=t(87),m=Object(c.a)(function(e){return{root:{width:"20%",marginTop:e.spacing(3),marginBottom:e.spacing(2)},table:{paddingLeft:"5px",paddingRight:"5px"},cell:{paddingLeft:"5px",paddingRight:"5px"}}});a.a=function(e,a){var t=m(),n=e.data.headers,c=e.data.data,p=!1;void 0!==c&&(p=c.length>0);var h=function(){if(void 0!==n)return n.map(function(e){return r.a.createElement(i.a,{key:e.name}," ",e.name," ")})},b=function(e,a){return Object.keys(e)[0]+a},f=function(){if(void 0!==c)return c.map(function(e,a){return r.a.createElement(u.a,{key:b(e,a)},n.map(function(a,n){return r.a.createElement(i.a,{key:n,align:"right",padding:"none"},r.a.createElement("div",{className:t.cell},function(e){var a=e.value;return"float"===e.type&&(a=Number(e.value).toFixed(3)),a}(e[a.key])))}))})};return r.a.createElement(d.a,{className:t.root},r.a.createElement("h4",null,e.header),p?r.a.createElement(l.a,{className:t.table},r.a.createElement(s.a,null,r.a.createElement(u.a,null,h())),r.a.createElement(o.a,null,f())):r.a.createElement("div",null," No data available "))}},97:function(e,a,t){e.exports=t(137)}},[[97,1,2]]]);
//# sourceMappingURL=main.165cf9ca.chunk.js.map