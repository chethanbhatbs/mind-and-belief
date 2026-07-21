// Shared chapter runtime: live page-number folio in the running foot.
(function(){
  var folio = document.getElementById('folio');
  if (!folio) return;
  function update(){
    var vh = window.innerHeight;
    var total = Math.max(1, Math.ceil(document.body.scrollHeight / vh));
    var cur = Math.min(total, Math.floor(window.scrollY / vh) + 1);
    folio.textContent = 'p. ' + cur + ' / ' + total;
  }
  addEventListener('scroll', update, {passive:true});
  addEventListener('resize', update);
  update();
})();
