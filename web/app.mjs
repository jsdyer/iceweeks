import {season, weeks, weekDates, match} from "./model.mjs";
const get = id => document.getElementById(id);
const week = get("week");
let charts = [], timer;
function text(tag, value, cls) {
  const e = document.createElement(tag); e.textContent=value;
  if (cls) e.className=cls;
  return e;
}
function dateLabel(iso) {return new Date(iso+"T00:00:00Z").toLocaleDateString("en-CA",{timeZone:"UTC",month:"short",day:"numeric"});}
function display(which, current) {
  const year = Number(get(which).value);
  const card = get("chart-"+which);
  const [start,end] = weekDates(year,current);
  const range = text("p",dateLabel(start)+" – "+dateLabel(end),"range");
  card.replaceChildren(range);
  const matches = match(charts,year,current);
  if (!matches.length) {
    card.append(text("p","No chart indexed for this week.","empty"));return;
  }
  const primary = matches[0];
  const img = document.createElement("img");
  img.alt = "Canadian Ice Service East Coast ice concentration chart issued " + primary.date;
  img.width = 800;img.height=619;
  img.addEventListener("error",()=>img.replaceWith(text("p","Preview unavailable. Open the original chart below.","empty")));
  img.src = primary.image;
  card.append(img);
  for (const c of matches) {
    const p = text("p","Issued "+c.date+" · ","source");
    const link = text("a","Open chart PDF"); link.href=c.pdf;
    p.append(link); card.append(p);
  }
}
function stop() {
  clearInterval(timer); timer = undefined; get("play").textContent="Play weeks";
}
function render() {
  const n = Number(week.value);
  get("week-label").textContent = "Week "+(n+1)+" of "+weeks;
  get("prev").disabled=n===0;get("next").disabled=n===weeks-1;
  display("first",n);display("second",n);
}
function step(by) {
  week.value = Math.max(0,Math.min(weeks-1, Number(week.value)+by));render();
  if (Number(week.value)===weeks-1) stop();
}
async function load() {
  const response = await fetch("./data/index.json");
  if (!response.ok) throw Error();
  const meta = await response.json(); charts = meta.charts;
  const years = [...new Set(charts.map(c=>season(c.date)))].sort((a,b)=>b-a);
  for (const [idx,id] of ["first","second"].entries()) {
    const sel = get(id);
    sel.replaceChildren(...years.map(y=>new Option(y+"–"+(y+1),y)));
    sel.value = years[Math.min(idx, years.length-1)];
    sel.addEventListener("change",()=>{stop();render();});
  }
  get("prev").onclick = ()=>{stop();step(-1);};
  get("next").onclick = ()=>{stop();step(1);};
  get("play").onclick = ()=>{
    if (timer) {stop();return;}
    if (Number(week.value)===weeks-1) {week.value=0;render();}
    get("play").textContent="Pause";timer=setInterval(()=>step(1),2200);
  };
  week.addEventListener("input",()=>{stop();render();});
  get("stamp").textContent = meta.count+" chart dates · "+meta.first+" to "+meta.latest+" · Index retrieved "+meta.retrieved+". Historical charts cover December through April. Images load from the Ice Logistics Portal archive.";
  render();
}
load().catch(()=>{get("stamp").textContent="Could not load chart dates. Reload the page or open the source catalogue.";});
