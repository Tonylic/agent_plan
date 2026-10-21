(function(){
  var cards=[].slice.call(document.querySelectorAll('.feat'));
  var state={ready:'',origin:'',q:''};
  var count=document.getElementById('fcount');
  function apply(){
    var q=state.q.trim().toLowerCase(),shown=0;
    cards.forEach(function(c){
      var ok=(!state.ready||c.getAttribute('data-ready')===state.ready)&&
             (!state.origin||c.getAttribute('data-origin')===state.origin)&&
             (!q||c.textContent.toLowerCase().indexOf(q)>=0);
      c.classList.toggle('hide',!ok);
      if(ok)shown++;
    });
    document.querySelectorAll('.grp').forEach(function(g){
      g.classList.toggle('empty',!g.querySelector('.feat:not(.hide)'));
    });
    if(count)count.textContent=(state.ready||state.origin||q)?shown+' of '+cards.length+' shown':cards.length+' items';
  }
  document.querySelectorAll('.fgrp').forEach(function(grp){
    var k=grp.getAttribute('data-k');
    grp.addEventListener('click',function(e){
      var b=e.target.closest('button');if(!b)return;
      state[k]=b.getAttribute('data-v');
      grp.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b);});
      apply();
    });
  });
  var q=document.getElementById('q');
  if(q)q.addEventListener('input',function(){state.q=q.value;apply();});
  apply();
  // A link to a hidden card clears the filters first.
  window.addEventListener('hashchange',function(){
    var t=document.getElementById(location.hash.slice(1));
    if(t&&t.classList.contains('hide')){
      state={ready:'',origin:'',q:''};if(q)q.value='';
      document.querySelectorAll('.fgrp').forEach(function(g){g.querySelectorAll('button').forEach(function(x,i){x.classList.toggle('on',i===0);});});
      apply();t.scrollIntoView();
    }
  });
  var links=[].slice.call(document.querySelectorAll('nav.toc a[href^="#"]'));
  var secs=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));}).filter(Boolean);
  if('IntersectionObserver' in window&&secs.length){
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(en.isIntersecting){links.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+en.target.id);});}
      });
    },{rootMargin:'-20% 0px -70% 0px'});
    secs.forEach(function(s){io.observe(s);});
  }
})();
