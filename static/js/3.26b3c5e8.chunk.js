(window["webpackJsonpcrypto-react"]=window["webpackJsonpcrypto-react"]||[]).push([[3],{235:function(a,e,t){"use strict";t.r(e);var r=t(8),d=t(0),s=t.n(d),c=t(40),n=t.n(c),l=null;var o={readCache:function(){return l},get:function(){return n.a.get("/api/getavailmarkets/").then(function(a){var e=a.data.results;l=e[0].exchange})}},u=t(213),h=t(32),i=t(171),b=Object(i.a)(function(a){return{root:{width:"20%",marginTop:a.spacing(3),marginBottom:a.spacing(2)},progress:{margin:a.spacing(2)},tablerow:{display:"flex",flexDirection:"row",justifyContent:"space-evenly"},table:{minWidth:650,padding:"10px"}}});e.default=function(a){var e=b(),t=Object(d.useState)(!0),c=Object(r.a)(t,2),l=c[0],i=c[1],m=(o.readCache(),Object(d.useState)([])),p=Object(r.a)(m,2),O=p[0],j=p[1],g=Object(d.useState)([]),v=Object(r.a)(g,2),f=v[0],E=(v[1],Object(d.useState)([])),w=Object(r.a)(E,2),S=w[0],x=(w[1],Object(d.useState)([])),y=Object(r.a)(x,2),C=y[0],k=(y[1],Object(d.useState)([])),A=Object(r.a)(k,2),B=A[0],M=(A[1],Object(d.useState)([])),N=Object(r.a)(M,2),T=N[0],D=(N[1],Object(d.useState)([])),J=Object(r.a)(D,2),G=J[0],I=(J[1],Object(d.useState)([])),L=Object(r.a)(I,2),U=L[0];L[1];return Object(d.useEffect)(function(){i(!0),n.a.post("/api/technicalssummary/",{exchange:a.exchange}).then(function(a){var e={};e.headers=a.data.topgainersheaders,e.data=a.data.topgainers,f.headers=a.data.toplosersheaders,f.data=a.data.toplosers,S.headers=a.data.unusualvolumeheaders,S.data=a.data.unusualvolume,C.headers=a.data.overboughtheaders,C.data=a.data.overbought,B.headers=a.data.oversoldheaders,B.data=a.data.oversold,T.headers=a.data.macdheaders,T.data=a.data.macd,U.headers=a.data.bullishmaheaders,U.data=a.data.bullishma,G.headers=a.data.bearishmaheaders,G.data=a.data.bearishma,j(e),i(!1)})},[a.exchange]),l?s.a.createElement(u.a,null):s.a.createElement("div",null,s.a.createElement("div",{className:e.tablerow},s.a.createElement(h.a,{data:O,header:"Top Gainers"}),s.a.createElement(h.a,{data:f,header:"Top Losers"}),s.a.createElement(h.a,{data:S,header:"Unusual Volume"})),s.a.createElement("div",{className:e.tablerow},s.a.createElement(h.a,{data:C,header:"Overbought"}),s.a.createElement(h.a,{data:B,header:"Oversold"}),s.a.createElement(h.a,{data:T,header:"MACD Indicator"})),s.a.createElement("div",{className:e.tablerow},s.a.createElement(h.a,{data:U,header:"Bullish MA"}),s.a.createElement(h.a,{data:G,header:"Bearish MA"})))}}}]);
//# sourceMappingURL=3.26b3c5e8.chunk.js.map