'use strict';
// Execute the ACTUAL shipped script in a small DOM contract, not a reimplementation.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('dist/app-reading.js','utf8');
assert.equal(source,fs.readFileSync('src/app.js','utf8'),'Shipped JavaScript must match source');
const html=fs.readFileSync('dist/index.html','utf8');
const data=JSON.parse(html.match(/id="edition-data" type="application\/json">(.*?)<\/script>/s)[1]);
const edition=html.match(/data-edition="([^"]+)"/)[1],sample=data[0];
const metadata=JSON.parse(html.match(/id="edition-search-meta" type="application\/json">(.*?)<\/script>/s)[1]);
function environment({query='',mobile=true,article=false,stored={},storageFails=false}={}){
 let doc;
 class Element{
  constructor(tag='div'){this.tag=tag;this.attributes={};this.dataset={};this.children=[];this.handlers={};this.hidden=false;this.textContent='';this.value='';this.target='';}
  setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return this.attributes[k]??null;}
  addEventListener(k,fn){(this.handlers[k]??=[]).push(fn);}fire(k,e={}){for(const fn of this.handlers[k]||[])fn(e);}
  append(...elements){this.children.push(...elements);}focus(){doc.activeElement=this;}
  querySelector(s){return this.selectors?.[s]||null;}contains(el){return this.children.includes(el);}
 }
 const loc=new URL('https://paper.example/'+(article?'edicao-'+edition+'/artigos/'+sample.id+'/':'')+query);
 const elements={};for(const selector of ['#search-panel','.search-toggle','.menu-toggle','#section-navigation','#search','#search-section','#search-type','#front-page','#filtered-page','#results-heading','#result-count','#empty','#results','#tool-status'])elements[selector]=new Element();
 elements['#search-panel'].action='https://paper.example/';elements['#search-panel'].hidden=true;
 const navlink=new Element('a');navlink.href='https://paper.example/editorias/pesquisa/';elements['#section-navigation'].children=[navlink];elements['#section-navigation'].selectors={'a':navlink};
 if(article){elements['[data-current-article]']=new Element();elements['[data-return-origin]']=new Element('a');elements['[data-return-origin]'].href='../../../editorias/pesquisa/';}
 else{elements['#edition-data']=new Element();elements['#edition-data'].textContent=JSON.stringify(data);elements['#edition-search-meta']=new Element();elements['#edition-search-meta'].textContent=JSON.stringify(metadata);}
 doc={body:{dataset:{edition}},activeElement:null,fonts:{ready:Promise.resolve()},handlers:{},querySelector:s=>elements[s]||null,querySelectorAll:s=>s==='.navrow a'?[navlink]:[],createElement:tag=>new Element(tag),addEventListener(k,fn){(this.handlers[k]??=[]).push(fn);},fire(k,e){for(const fn of this.handlers[k]||[])fn(e);}};
 const storage={...stored},media={matches:mobile,addEventListener(k,fn){this.change=fn;}};
 const win={handlers:{},matchMedia:()=>media,scrollY:540,scrollTo(args){this.scroll=args;},print(){this.printed=true;},addEventListener(k,fn){this.handlers[k]=fn;}};
 const context=vm.createContext({window:win,document:doc,location:loc,URL,URLSearchParams,Date,Promise,requestAnimationFrame:fn=>fn(),navigator:{clipboard:{writeText:async()=>{}}},sessionStorage:{getItem:k=>{if(storageFails)throw Error('disabled');return storage[k]||null;},setItem:(k,v)=>{if(storageFails)throw Error('disabled');storage[k]=v;},removeItem:k=>delete storage[k]}});
 vm.runInContext(source,context);return {doc,win,elements,media,storage,navlink,Element,loc};
}
let count=0;function check(name,fn){fn();count++;console.log('PASS '+name);}
check('mobile Cadernos opens, focuses, Escape closes and restores trigger',()=>{
 const e=environment();assert.equal(e.elements['#section-navigation'].hidden,true);assert.equal(e.elements['.menu-toggle'].hidden,false);
 e.elements['.menu-toggle'].fire('click');assert.equal(e.elements['#section-navigation'].hidden,false);assert.equal(e.doc.activeElement,e.navlink);
 e.doc.fire('keydown',{key:'Escape',preventDefault(){}});assert.equal(e.elements['#section-navigation'].hidden,true);assert.equal(e.doc.activeElement,e.elements['.menu-toggle']);
});
check('Buscar is independently reachable; focus and Escape work',()=>{
 const e=environment();e.elements['.menu-toggle'].fire('click');e.elements['.search-toggle'].fire('click');assert.equal(e.elements['#section-navigation'].hidden,true);assert.equal(e.elements['#search-panel'].hidden,false);assert.equal(e.doc.activeElement,e.elements['#search']);
 e.doc.fire('keydown',{key:'Escape',preventDefault(){}});assert.equal(e.doc.activeElement,e.elements['.search-toggle']);assert.equal(e.elements['#search-panel'].hidden,true);
});
check('viewport change never leaves focus in hidden cadernos',()=>{
 const e=environment({mobile:false});assert.equal(e.elements['#section-navigation'].hidden,false);e.navlink.focus();e.media.matches=true;e.media.change();assert.equal(e.doc.activeElement,e.elements['.menu-toggle']);
});
check('search indexes all96; each section exactly16',()=>{
 const e=environment({query:'?q='});assert.equal(e.elements['#results'].children.length,96);
 for(const section of new Set(data.map(a=>a.section)))assert.equal(e.win.TMTReading.rankArticles(data.map(a=>({...a,...metadata[a.id]})),'',section).length,16);
});
check('type/section intersection filters actual shipped results',()=>{
 const e=environment({query:'?q=&secao=pesquisa&tipo=noticia'});assert.equal(e.elements['#results'].children.length,data.filter(a=>a.section==='pesquisa'&&e.win.TMTReading.typeKey(metadata[a.id].contentType)==='noticia').length);assert.equal(e.elements['#search-section'].value,'pesquisa');assert.equal(e.elements['#search-type'].value,'noticia');
 const guides=environment({query:'?q=&secao=instituicoes&tipo=guia'});assert.equal(guides.elements['#results'].children.length,data.filter(a=>a.section==='instituicoes'&&guides.win.TMTReading.typeKey(metadata[a.id].contentType)==='guia').length);
});
check('diacritics, token matches and title relevance',()=>{
 const e=environment();const rows=[{id:'body',title:'Outro assunto',deck:'',paragraphs:['coração'],contentType:'Guia'},{id:'title',title:'Coração e cuidado',deck:'',paragraphs:[],contentType:'Guia'}];assert.equal(e.win.TMTReading.rankArticles(rows,'coracao')[0].id,'title');assert.equal(e.win.TMTReading.rankArticles(rows,'coracao cuidado').length,1);
});
check('empty results are announced and not replaced with unrelated content',()=>{
 const e=environment({query:'?q=zzzzzzzzzzzzzz'});assert.equal(e.elements['#results'].children.length,0);assert.equal(e.elements['#empty'].hidden,false);assert.ok(e.elements['#result-count'].textContent.includes('0 matérias'));
});
check('results show actual date/type/time and honest CTA',()=>{
 const e=environment({query:'?q='+encodeURIComponent(sample.title)}),result=e.elements['#results'].children[0];assert.ok(result.children[0].textContent.includes(metadata[sample.id].typeLabel));assert.ok(result.children[3].textContent.includes(metadata[sample.id].dateLabel));assert.ok(result.children[3].textContent.includes('min de leitura'));assert.equal(result.children[4].textContent,'Ler matéria e fontes →');
});
check('safe origin rejects external, script, unrelated, stale and malformed targets',()=>{
 const e=environment(),base={edition,y:40,at:Date.now(),url:'/editorias/pesquisa/'};assert.ok(e.win.TMTReading.safeOrigin(base));
 for(const patch of [{url:'https://evil.example/'},{url:'javascript:alert(1)'},{url:'/sobre/'},{edition:'invalid-edition'},{y:-1},{at:0},{url:'/editorias/pesquisa/../../sobre/'}])assert.equal(e.win.TMTReading.safeOrigin({...base,...patch}),null);
});
check('origin captured only from current local navigation',()=>{
 const e=environment();const link=new e.Element('a');link.href='https://paper.example/edicao-'+edition+'/artigos/'+sample.id+'/';link.closest=()=>({dataset:{articleId:sample.id}});
 e.doc.fire('click',{button:0,target:{closest:()=>link}});const record=JSON.parse(e.storage['tmt:reading-origin:'+edition]);assert.equal(record.y,540);assert.equal(record.url,'/');
});
check('return link restores exact origin instead of guessing browser history',()=>{
 const state={edition,url:'/?q=cancer',y:810,at:Date.now(),articleId:sample.id},e=environment({article:true,stored:{['tmt:reading-origin:'+edition]:JSON.stringify(state)}});
 assert.equal(e.elements['[data-return-origin]'].href,'/?q=cancer');e.elements['[data-return-origin]'].fire('click',{button:0});assert.equal(JSON.parse(e.storage['tmt:reading-return:'+edition]).y,810);
});
check('disabled session storage keeps section fallback and search usable',()=>{const e=environment({article:true,storageFails:true});assert.equal(e.elements['[data-return-origin]'].href,'../../../editorias/pesquisa/');});
(async()=>{
 const state={edition,url:'/?q=cancer',y:810,at:Date.now()},e=environment({query:'?q=cancer',stored:{['tmt:reading-return:'+edition]:JSON.stringify(state)}});e.win.handlers.pageshow();await new Promise(resolve=>setImmediate(resolve));assert.equal(e.win.scroll.top,810);assert.equal(e.storage['tmt:reading-return:'+edition],undefined);count++;console.log('PASS explicit-return pageshow restores once after fonts');console.log(count+' behavioral tests passed against dist/app-reading.js');
})().catch(error=>{console.error(error);process.exitCode=1;});
