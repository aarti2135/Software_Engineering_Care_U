async function proFetchAlerts(){
  try{
    const resp = await fetch("/proactive/alerts/unread/");
    if(!resp.ok) return;
    const data = await resp.json();
    const items = data.alerts || [];
    const countEl = document.getElementById("alerts-count");
    if(countEl) countEl.innerText = items.length;

    const ul = document.getElementById("alerts-items");
    if(ul){ ul.innerHTML = ""; }
    (items || []).forEach(a=>{
      if(ul){
        const li = document.createElement("li");
        li.textContent = a.message;
        li.style.cursor = "pointer";
        li.onclick = ()=>proMarkRead(a.id);
        ul.appendChild(li);
      }
      proToast(a.message);
    });
  }catch(e){}
}
async function proMarkRead(id){ try{ await fetch(`/proactive/alerts/mark-read/${id}/`); }catch(e){} proFetchAlerts(); }
function proToggleAlerts(){
  const m = document.getElementById("alerts-menu");
  if(m) m.style.display = (m.style.display==="none" || !m.style.display) ? "block" : "none";
}
function proToast(msg){
  const t = document.createElement("div");
  t.textContent = msg;
  t.style.position="fixed"; t.style.right="16px"; t.style.bottom="16px";
  t.style.padding="10px"; t.style.border="1px solid #333"; t.style.background="#fff";
  document.body.appendChild(t); setTimeout(()=>t.remove(),4000);
}
document.addEventListener("DOMContentLoaded", ()=>{ proFetchAlerts(); setInterval(proFetchAlerts, 10000); });
