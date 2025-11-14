document.addEventListener('DOMContentLoaded', function(){
  const select = document.getElementById('hostelSelect');
  const newFields = document.getElementById('newHostelFields');
  if(!select) return;
  function toggle(){
    if(select.value === '__new__') newFields.style.display = 'block';
    else newFields.style.display = 'none';
  }
  select.addEventListener('change', toggle);
  toggle();
});
