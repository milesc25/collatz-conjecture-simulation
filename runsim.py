import math, random
import numpy as np
from matplotlib.colors import hsv_to_rgb
import plotly.graph_objects as go

def collatz_next(n):
    return n//2 if n%2 == 0 else (3*n)+1
def build_trajectories(N):
    trajs={}
    stimes={}
    seen=set()
    for n in range(1,N+1):
        seq=[n]
        a=n
        steps=0
        while a!= 1 and a<=10**7 and steps<2000:
            a = collatz_next(a)
            seq.append(a)
            seen.add(a)
            steps+=1
        trajs[n]=seq
        stimes[n]=len(seq)-1
        seen.update(seq)
    return trajs,stimes,seen
def build_coords(seen,k):
    sbits=2**k
    mlog=math.log(max(seen)) if seen else 1.0
    coords={}
    for v in seen:
        low= v&(sbits-1)
        mid=(v>>k)&(sbits - 1)
        theta= 2*math.pi*(low/sbits)
        phi= 2*math.pi*(mid/sbits)
        ln= math.log(v)/(mlog+1e-12)
        r= 0.3+0.4*ln
        cp= math.cos(phi)
        coords[v]=(r*math.cos(theta)*(0.8+0.2*cp),  r*math.sin(theta)*(0.8+0.2*cp),0.3*math.sin(phi)+0.5*ln)
    return coords

def build_web_trace(trajs,coords,max_lines=8000):
    xs,ys,zs=[], [], []
    lc=0
    for seq in trajs.values():
        if lc>=max_lines:
            break
        step=max(1,len(seq)//30)
        for i in range(0,len(seq)-1,step):
            a,b =seq[i],seq[i+1]
            if a in coords and b in coords:
                xa,ya,za= coords[a]
                xb,yb,zb= coords[b]
                xs+=[xa,xb,None]
                ys+=[ya,yb,None]
                zs+=[za,zb,None]
                lc+=1
                if lc>=max_lines:
                    break
    return go.Scatter3d(x=xs,y=ys,z=zs,mode='lines', line=dict(color='cyan',width=1),opacity=0.08, hoverinfo='none',showlegend=False)
def pick_samples(trajs,stimes,S,N):
    sset=set()
    p=1
    while p<=N:
        sset.add(p)
        p*=2
    for n, _ in sorted(stimes.items(),key=lambda x: -x[1])[:S//3]:
        sset.add(n)
    i=1
    while len(sset)<S and i<= N:
        if i%max(1,N//(S*2)) == 0:
            sset.add(i)
        i+=1
    while len(sset)<S:
        sset.add(random.randint(1,N))
    return sorted(sset)[:S]
def interp(pts,tf):
    total = len(pts) - 1
    if tf<=0 or total <= 0: return pts[0]
    if tf>=1: return pts[-1]
    pos=tf*total
    i=int(pos)
    f=pos-i
    pi,pj = pts[i],pts[min(i+1,total)]
    return (pi[0]*(1-f)+pj[0]*f, pi[1]*(1-f)+pj[1]*f, pi[2]*(1-f)+pj[2]*f)
def tohex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
def build_figure(N,S,k,max_frames,trail_len,progress_cb=None):
    def status(msg):
        if progress_cb: progress_cb(msg)
        else: print(msg)
    status("computing sequences")
    trajs,stimes,seen= build_trajectories(N)

    status("mapping ints")
    coords = build_coords(seen,k)

    status("selecting samples")
    slist=pick_samples(trajs,stimes,S,N)
    tdata=[]
    for n in slist:
        pts=[coords[v] for v in trajs[n] if v in coords]
        col=tohex(hsv_to_rgb([(stimes[n]/200) % 1.0, 0.8, 0.9]))
        tdata.append({'pts':pts, 'L':len(pts), 'col':col})
    maxL=max((d['L'] for d in tdata),default=1)
    Sn=len(tdata)
    clist = list(coords.values())
    xr= [min(c[0] for c in clist)-0.15,max(c[0] for c in clist)+0.15]
    yr= [min(c[1] for c in clist)-0.15,max(c[1] for c in clist)+0.15]
    zr= [min(c[2] for c in clist)-0.15,max(c[2] for c in clist)+0.15]
    ax,ay,az=coords.get(1,(0,0,0))
    attr=go.Scatter3d(x=[ax],y=[ay],z=[az],mode='markers',marker=dict(size=7,color='yellow',symbol='diamond',line=dict(color='orange', width=2)),
                      hovertemplate='Attractor: 1<extra></extra>', showlegend=False)

    def mktrace(d,t):
        pts=d['pts']
        L=d['L']
        col=d['col']
        scale=(L/maxL)**0.5
        tsc=min(1.0,t/(scale*0.8+0.2))
        tend=max(1,min(int(tsc*L),L-1))
        done=tend>=L-1
        if done:
            return go.Scatter3d(x=[ax],y=[ay],z=[az], mode='markers',
                marker=dict(size=0,color=col),hoverinfo='none',showlegend=False)
        dot= interp(pts,tsc)
        tstart=max(0,tend-trail_len)
        tpts=pts[tstart:tend+1]
        if len(tpts)>=2:
            tx=[p[0] for p in tpts]+[dot[0]]
            ty=[p[1] for p in tpts]+[dot[1]]
            tz=[p[2] for p in tpts]+[dot[2]]
            sz=[0]*len(tpts)+[5]
            return go.Scatter3d(x=tx,y=ty,z=tz,mode='lines+markers',line=dict(color=col,width=2),marker=dict(size=sz,color=col,line=dict(color='white',width=0.5)),
                opacity=0.8,hoverinfo='none',showlegend=False)
        else:
            return go.Scatter3d(x=[dot[0]],y=[dot[1]],z=[dot[2]],mode='markers',marker=dict(size=5,color=col,line=dict(color='white',width=0.5)),
                opacity=0.8,hoverinfo='none',showlegend=False)
    status("creating init frame")
    tinit= [mktrace(d,0.0) for d in tdata]
    allt=[attr]+tinit
    anim= list(range(1,1+Sn))
    status(f"creating {max_frames} frames")
    frames=[]
    for fi in range(max_frames):
        t =fi/max(max_frames-1,1)
        frames.append(go.Frame(
            data=[mktrace(d,t) for d in tdata],
            traces=anim,name=str(fi)))


    scene=dict(
        xaxis= dict(range=xr,showgrid=False,zeroline=False,showticklabels=False,backgroundcolor='black', title=''),
        yaxis= dict(range=yr,showgrid=False,zeroline=False,showticklabels=False,backgroundcolor='black', title=''),
        zaxis= dict(range=zr,showgrid=False,zeroline=False,showticklabels=False,backgroundcolor='black', title=''),
        bgcolor='black',camera=dict(eye=dict(x=1.4,y=1.4,z=0.7)), aspectmode='cube')
    #fix this layout later
    layout = go.Layout(scene=scene,paper_bgcolor='black',plot_bgcolor='black',
        margin=dict(l=0,r=0,t=30,b=0),showlegend=False,
        updatemenus=[dict(type='buttons',showactive=False,
            bgcolor='#222',bordercolor='#444',font=dict(color='white'),
            y=0.02, x=0.5, xanchor='center',
            buttons=[
                dict(label='▶ play', method='animate',
                    args=[None,dict(frame=dict(duration=50,redraw=True),fromcurrent=True,mode='immediate')]),
                dict(label='⏸ pause', method='animate',
                    args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')])])],
        sliders=[dict(
            currentvalue=dict(prefix='Frame: ',visible=True,xanchor='center',font=dict(color='white')),
            bgcolor='#333',bordercolor='#555',tickcolor='#555',font=dict(color='white'),
            pad=dict(t=50),
            steps=[dict(method='animate',
                args=[[str(i)],dict(mode='immediate',frame=dict(duration=0,redraw=True))],
                label='') for i in range(max_frames)])],
        annotations=[dict(text=f"N={N}  ·  {len(trajs):,} sequences  ·  S={Sn}  ·  k={k}  ·  {max_frames} frames",
            xref='paper',yref='paper',x=0.5,y=1.01,
            showarrow=False,font=dict(color='#888',size=11))])
    fig=go.Figure(data=allt,layout=layout,frames=frames)
    status("finished")
    return fig,{'n_sequences':len(trajs),'n_unique':len(seen)}
if __name__ == "__main__":
    fig,info = build_figure(N=1000,S=50,k=11,max_frames=150,trail_len=20)
    out="collatz_orbits.html"
    fig.write_html(out)
    print(f"saved to {out}")
    print(f"  {info['n_sequences']:,} sequences · {info['n_unique']:,} unique integers")