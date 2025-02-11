# RadArt

### Project creators:
1. Burzars<br />
2. sval9ka07<br />
3. MIPTestet<br />
4. sergevkim<br />
5. sayheykid<br />
6. aleksanderkarpov<br />

## Installation

```
pip install -e .

```


## Download data:
```
bash scripts/download_data.sh
```

## Run scripts

### Calculate metrics:
```
python scripts/calc_metrics.py
```

### Launch visualizations:
```
python scripts/launch_vis.py
```

### Project architecture:
```
├── LICENSE                                    <- Our MIT license.
├── README.md                                  <- The top-level README for developers using this project.
├── notebooks                                  <- Jupyter notebooks.
│   ├── delays_and_speedcolors_launcher.ipynb
│   ├── main.ipynb
│   └── reflectance_launcher.ipynb
│
├── radart                                     <- Source code for use in this project.
│   ├── core                                   <- Core functionality.
│   │   ├── __init__.py  
│   │   ├── lidar_denoiser.py                  <- Removes unnecessary noise from lidar data.
│   │   └── synchronization.py                 <- Shifts radar data to a single timestamp.
│   │
│   ├── metrics                                <- Metrics for evaluation.
│   │   ├── __init__.py
│   │   └── metrics.py 
│   │
│   ├── utils                                  <- Utility scripts.
│   │   ├── __init__.py
│   │   └── preprocessing.py
│   │
│   ├── visual                                 <- Visualization scripts.
│   │   ├── __init__.py
│   │   ├── delay_variety.py
│   │   ├── delays_and_speedcol...
│   │   ├── paint_reflectance.py
│   │   ├── radild_func.py
│   │   └── test_output.html
│   │   
│   │
│   └── scripts                                <- Scripts for launching tasks.
│       ├── launcher_1.py
│       ├── launcher_2.py
│       └── launcher_dash.py
│
├── requirements.txt                           <- The requirements file for reproducing the project environment.
└── setup.py                                   <- makes project pip installable (pip install -e .)
```
