import json

with open('all_plots.json', 'r') as f:
    plots = json.load(f)

# Left diagonal boundary equations (derived from plot left-edge positions):
# Plots 6-7:  x = 22.5 - 0.1*y
# Plots 8-15: x = 28.833 - 0.1515*y
# Plot 1:     x = 21.5 - 0.065*y (approximate)

def diag_left(y):
    if y < 25:
        return 21.5 - 0.065 * y
    elif y < 52:
        return 22.5 - 0.1 * y
    else:
        return 28.833 - 0.1515 * y

# Only these plots actually sit on the left diagonal boundary:
# Plot 1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
# Plots 2-5 are interior plots within the top triangle - NOT on the diagonal
diag_plot_labels = {'1'} | set(str(i) for i in range(6, 16))

processed_plots = []
for p in plots:
    pp = dict(p)

    if pp['lbl'] in diag_plot_labels:
        top_y = pp['top']
        bot_y = pp['top'] + pp['height']
        x_top = diag_left(top_y)   # boundary at top of plot (further right)
        x_bot = diag_left(bot_y)   # boundary at bottom of plot (further left)

        # Position div at the leftmost point (bottom diagonal)
        orig_right = pp['left'] + pp['width']
        new_left = x_bot
        new_width = orig_right - new_left

        if new_width > 0:
            # Clip off upper-left triangle
            indent_pct = (x_top - x_bot) / new_width * 100
            indent_pct = max(0, min(50, indent_pct))

            pp['left'] = round(new_left, 3)
            pp['width'] = round(new_width, 3)
            pp['clip'] = f"polygon({indent_pct:.1f}% 0%, 100% 0%, 100% 100%, 0% 100%)"

    processed_plots.append(pp)

clips = sum(1 for p in processed_plots if 'clip' in p)
print(f"Total plots: {len(processed_plots)}, with clip-path: {clips}")
for p in processed_plots:
    if 'clip' in p:
        r = p['left'] + p['width']
        print(f"  Plot {p['lbl']}: L={p['left']:.2f}% W={p['width']:.2f}% R={r:.2f}% clip={p['clip']}")


def gen_html(plots_data):
    counts = {'available': 0, 'sold': 0, 'booked': 0, 'registered': 0}
    for p in plots_data:
        counts[p['st']] = counts.get(p['st'], 0) + 1
    total = sum(counts.values())

    plot_divs = []
    for p in plots_data:
        style_parts = [
            f"left:{p['left']:.3f}%",
            f"top:{p['top']:.3f}%",
            f"width:{p['width']:.3f}%",
            f"height:{p['height']:.3f}%"
        ]
        if 'clip' in p:
            style_parts.append(f"clip-path:{p['clip']}")

        style = ';'.join(style_parts)
        data = json.dumps({"lbl": p['lbl'], "st": p['st'], "sqyd": p.get('sqyd', '400')})
        data_escaped = data.replace('"', '&quot;')
        div = f'<div class="pl st-{p["st"]}" style="{style}" data-p="{data_escaped}" onclick="sp(this)"></div>'
        plot_divs.append(div)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rachakonda Layout \u2013 Interactive Plan</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;500;600&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,sans-serif;background:#0c1c2e;color:#e2edf5;min-height:100vh}}
header{{background:linear-gradient(135deg,#091929,#12344d);padding:10px 20px;display:flex;
  align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;
  border-bottom:2px solid #c8a84b;box-shadow:0 3px 16px rgba(0,0,0,.5)}}
.brand h1{{font-family:Rajdhani,sans-serif;font-size:1.2rem;font-weight:700;color:#c8a84b}}
.brand p{{font-size:.65rem;color:#7eaec8;margin-top:1px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 12px}}
.leg{{display:flex;align-items:center;gap:4px;font-size:.65rem;font-weight:600;text-transform:uppercase}}
.dot{{width:11px;height:11px;border-radius:3px;border:1px solid rgba(255,255,255,.3)}}
.bar{{max-width:1100px;margin:10px auto;padding:0 12px;display:flex;gap:8px;flex-wrap:wrap}}
.sc{{flex:1;min-width:75px;background:#0f2235;border:1px solid #1e3d5c;border-radius:8px;padding:7px 10px;text-align:center}}
.sn{{font-family:Rajdhani,sans-serif;font-size:1.5rem;font-weight:700;color:#c8a84b;line-height:1}}
.sl{{font-size:.58rem;text-transform:uppercase;letter-spacing:.6px;color:#6a96b8;margin-top:2px}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 12px 20px}}
.hint{{text-align:center;font-size:.68rem;color:#5a86a8;margin-bottom:6px}}
.mapbox{{position:relative;width:100%;border:2px solid #1e3d5c;border-radius:8px;overflow:hidden;
  box-shadow:0 6px 30px rgba(0,0,0,.6);background:#162a3e}}
.mapbox img.bg{{width:100%;height:auto;display:block}}
.pl{{position:absolute;cursor:pointer;border-radius:1px;
  transition:background .15s,border .15s,box-shadow .15s;z-index:2}}
.pl:hover{{background:rgba(60,140,255,0.35)!important;border:1.5px solid #4a9eff!important;z-index:10!important;
  box-shadow:0 0 8px rgba(74,158,255,0.5)}}
.pl.sel{{background:rgba(200,168,75,0.35)!important;border:2px solid #c8a84b!important;z-index:11!important;
  box-shadow:0 0 16px rgba(200,168,75,0.8)}}
.st-available{{background:rgba(0,0,0,0);border:1px solid rgba(100,180,255,0.15)}}
.st-sold{{background:rgba(195,54,255,0.1);border:1px solid rgba(195,54,255,0.35)}}
.st-booked{{background:rgba(252,193,255,0.1);border:1px solid rgba(252,193,255,0.35)}}
.st-registered{{background:rgba(194,54,254,0.1);border:1px solid rgba(194,54,254,0.35)}}
.bd{{display:none;position:fixed;inset:0;z-index:300;background:rgba(0,0,0,.7);
  backdrop-filter:blur(6px);align-items:center;justify-content:center}}
.bd.on{{display:flex}}
.mo{{background:linear-gradient(145deg,#0c2040,#142d4a);border:1px solid #2a5078;
  border-radius:14px;padding:24px 26px 20px;width:90%;max-width:360px;
  box-shadow:0 20px 60px rgba(0,0,0,.9);position:relative;animation:pop .18s ease}}
@keyframes pop{{from{{transform:scale(.85);opacity:0}}to{{transform:scale(1);opacity:1}}}}
.mc{{position:absolute;top:8px;right:12px;background:none;border:none;color:#6a96b8;
  font-size:1.5rem;cursor:pointer;padding:2px 6px}}
.mc:hover{{color:#fff}}
.mbadge{{display:inline-block;background:#c8a84b;color:#0a1828;font-family:Rajdhani,sans-serif;
  font-size:1.6rem;font-weight:700;padding:2px 14px;border-radius:5px;margin-bottom:6px}}
.mpill{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.67rem;
  font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-bottom:12px}}
.pa{{background:#cbff96;color:#163400}}.ps{{background:#c336ff;color:#fff}}
.pb{{background:#fcc1ff;color:#4a0060}}.pr{{background:#c236fe;color:#fff}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.dc{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:6px;padding:8px 10px}}
.dl{{font-size:.58rem;text-transform:uppercase;letter-spacing:.7px;color:#6a96b8;margin-bottom:2px}}
.dv{{font-family:Rajdhani,sans-serif;font-size:.9rem;font-weight:600;color:#e2edf5}}
.cta{{margin-top:14px;width:100%;padding:10px;border:none;border-radius:8px;
  background:linear-gradient(135deg,#c8a84b,#a07828);color:#0a1828;
  font-family:Rajdhani,sans-serif;font-size:.9rem;font-weight:700;cursor:pointer;
  transition:transform .15s,box-shadow .15s;letter-spacing:.5px}}
.cta:hover{{transform:translateY(-2px);box-shadow:0 5px 16px rgba(200,168,75,.4)}}
.cta.na{{background:#1e1e1e!important;color:#666!important;cursor:default}}
.cta.na:hover{{transform:none;box-shadow:none}}
footer{{text-align:center;padding:10px;font-size:.62rem;color:#3a6088;border-top:1px solid #1a3355;margin-top:4px}}
</style>
</head>
<body>
<header>
  <div class="brand">
    <h1>LOHITHA DHARMA PROJECTS PVT. LTD.</h1>
    <p>Rachakonda Village &middot; Pullalacheruvu Mandal &middot; Prakasham District &middot; Interactive Layout Plan</p>
  </div>
  <div class="legend">
    <div class="leg"><div class="dot" style="background:#3d8c40"></div>Available</div>
    <div class="leg"><div class="dot" style="background:#9b2d9b"></div>Sold Out</div>
    <div class="leg"><div class="dot" style="background:#c060c0"></div>Booked</div>
    <div class="leg"><div class="dot" style="background:#7b34b8"></div>Registered</div>
  </div>
</header>
<div class="bar">
  <div class="sc"><div class="sn" id="cA">{counts['available']}</div><div class="sl">Available</div></div>
  <div class="sc"><div class="sn" id="cS">{counts['sold']}</div><div class="sl">Sold Out</div></div>
  <div class="sc"><div class="sn" id="cB">{counts['booked']}</div><div class="sl">Booked</div></div>
  <div class="sc"><div class="sn" id="cR">{counts['registered']}</div><div class="sl">Registered</div></div>
  <div class="sc"><div class="sn" id="cT">{total}</div><div class="sl">Total Plots</div></div>
</div>
<div class="wrap">
  <p class="hint">Click any plot to view details</p>
  <div class="mapbox" id="lm">
    <img class="bg" src="layout-plan.png" alt="Rachakonda Layout Plan">
{chr(10).join('    ' + d for d in plot_divs)}
  </div>
</div>
<div class="bd" id="bd">
  <div class="mo">
    <button class="mc" onclick="cl()">&#215;</button>
    <div class="mbadge" id="mN">Plot &#8212;</div><br>
    <span class="mpill" id="mP">&#8212;</span>
    <div class="g2">
      <div class="dc"><div class="dl">Plot No.</div><div class="dv" id="mI">&#8212;</div></div>
      <div class="dc"><div class="dl">Status</div><div class="dv" id="mS">&#8212;</div></div>
      <div class="dc"><div class="dl">Mandal</div><div class="dv">Pullalacheruvu</div></div>
      <div class="dc"><div class="dl">District</div><div class="dv">Prakasham</div></div>
    </div>
    <button class="cta" id="mC" onclick="eq()">Enquire About This Plot</button>
  </div>
</div>
<footer>&copy; Lohitha Dharma Projects Pvt. Ltd. &middot; Interactive Layout Plan &middot; All figures approximate</footer>
<script>
const SL={{available:'Available',sold:'Sold Out',booked:'Booked',registered:'Registered'}};
const PC={{available:'pa',sold:'ps',booked:'pb',registered:'pr'}};
let cur=null,cd=null;
function sp(el){{
  if(cur)cur.classList.remove('sel');
  cur=el;el.classList.add('sel');
  const d=JSON.parse(el.getAttribute('data-p'));cd=d;
  document.getElementById('mN').textContent='Plot '+d.lbl;
  const p=document.getElementById('mP'),st=d.st||'available';
  p.textContent=SL[st]||st;p.className='mpill '+(PC[st]||'pa');
  document.getElementById('mI').textContent=d.lbl;
  document.getElementById('mS').textContent=SL[st]||st;
  const c=document.getElementById('mC');
  if(st==='available'){{c.textContent='\\ud83d\\udcde Enquire About This Plot';c.className='cta';}}
  else{{c.textContent='\\u2713 '+(SL[st]||st);c.className='cta na';}}
  document.getElementById('bd').classList.add('on');
}}
function cl(){{document.getElementById('bd').classList.remove('on');if(cur){{cur.classList.remove('sel');cur=null;}}}}
function eq(){{if(cd&&cd.st==='available')alert('Please contact us about Plot '+cd.lbl+'.\\n\\nLohitha Dharma Projects Pvt. Ltd.');}}
document.getElementById('bd').addEventListener('click',e=>{{if(e.target.id==='bd')cl();}});
document.addEventListener('keydown',e=>{{if(e.key==='Escape')cl();}});
</script>
</body>
</html>'''
    return html

html = gen_html(processed_plots)
with open('plot.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nGenerated plot.html ({len(html)} bytes) with {len(processed_plots)} plots")
