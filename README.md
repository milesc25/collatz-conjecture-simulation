# Collatz Conjecture Orbit Simulation

A 3D web app visualization of Collatz sequences. Each integer from 1 to N is mapped to a point in space based on its binary structure and logarithm, then animated as it travels its Collatz path toward the attractor at 1.

USE THE WEB APP: 

## How it works

Each int is embedded in 3D space: its lowest bits determine angular position, and its log determines radial depth/height. A sample of trajectories is then simuated and each one traces its actual Collatz path through that space until it converges to the attractor.

Here are the parameters:
- **N** — integer range (1..N)
- **S** — # of animated trajectories
- **k** — bit depth for the coordinate mapping
- **Frames / Trail length** — animation detail

## Running

### Streamlit app
```bash
pip install -r requirements.txt
streamlit run app.py
```

### CLI (outputs an interactive HTML file)
```bash
python runsim.py
```