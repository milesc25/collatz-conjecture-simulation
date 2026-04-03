import streamlit as st
from runsim import build_figure

st.set_page_config(page_title="Collatz Orbits", layout="centered")
st.title("Collatz Orbits")
st.caption("A 3D simulation of Collatz trajectories converging toward the attractor at 1")
st.sidebar.header("Parameters")
N=st.sidebar.slider("N — integer range",100,10000,1000,100)
S=st.sidebar.slider("S — trajectories animated",10,200,50,5)
k=st.sidebar.slider("k — bit depth",6,16,11,1)
max_frames=st.sidebar.slider("frames",30,300,120,10)
trail_len=st.sidebar.slider("Trail length",5,60,15,5)
st.sidebar.info("press Render to build the animation. all rendering is done in the browser with WebGL.")
run = st.sidebar.button("Render", type="primary", use_container_width=True)
if run:
    status = st.empty()
    fig, info = build_figure(N=N,S=S,k=k, max_frames=max_frames, trail_len=trail_len, progress_cb=lambda msg: status.text(msg),)
    status.empty()
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{info['n_sequences']:,} sequences · {info['n_unique']:,} unique integers · " f"{max_frames} frames · trail={trail_len}")
else:
    st.info("adjust parameters to your liking, then press **Render**.")