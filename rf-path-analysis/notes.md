testing directory ~/Downloads/splat-path-analysis/

srtm2sdf expects SRTM3 input data (.hgt files, 3arc-second/90meter resolution), each file a 1degree x 1degree square
https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL3.003/2000.02.11/
since there are 3600 arc-seconds per degree, and we are operating at 3arc-second resolution,
this tool outputs a 1200x1200 grid. it has a newline for each point, so it is a 1,440,000 line file
(actually +4 lines for some header info)

srtm2sdf-hd expects SRTM1 input data (.hgt files, 1arc-second/30meter resolution)
https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/
- outputs 3600x3600 grid, so file is 12,960,000 lines long lol

SPLAT:
-p, -e, -h, -H, -l, and -o are all options that spit out a .png (-o spits out a .ppm)
I personally think -H and -o are the most helpful

`splat -t input/apt.qth -r input/dickerman.qth -d ./terrain/sdf3 -H H -o o`

also spits out an "apartment-to-dickerman.txt" which gives an expected signal level (in dBm) at the other side
- this is probably the value I will use to make a go-or-no-go decision
the .png output from the -H command gives a nice graph and an azimuth to aim for, so I could maybe include that in the phone notification I get for a summit?


`./src/splat-1.4.2/splat-hd -t input/apt.qth -r input/dickerman-1arc-height.qth  -d ./terrain/sdf1 -H h -o o`



`rm *.txt *.png *.ppm` is a helpful command to clean the current directory of output files

vim tries to use tar when opening .lrp files, even though for SPLAT they are just ASCII
`vim --cmd "let g:loaded_tarPlugin = 1" -b apt.lrp`


there is an AUR package for splat, but it only comes with splat (3arc-second), not splat-hd (1arc-second)
so downloaded+built a source copy to be able to use splat-hd

srtm2sdf-hd is a symlink to srtm2sdf, the binary probably has logic to behave differently based on the filename it was invoked as (similar to e.g. busybox)





because the terrain models only have 30m resolution, they do not accurately capture the proper summit elevation. there are 2 strategies then:
- set the AGL amount so as to put the antenna at the real elevation. e.g. for kelly butte, the terrain pixel is ~5330ft, but the actual elevation is 5420ft. AGL = 90ft
- set the AGL to 5ft over ground (expected height when held by someone) to ensure ground effect is properly accounted for

not sure how big of a difference this makes, so I compared 2 examples. kelly butte difference between actual and terrain pixel is 90ft, mount dickerman difference is 30ft

path loss due to terrain shielding:

            5ft         realelev
kelly       56.63db     34.80db
dickerman   33.52db     33.51db

(fwiw, SPLAT reports kelly as double-horizon diffraction dominant, and dickerman as single-horizon diffraction dominant)

(free space path loss is similar for both of these mountains)
the standing-height (5ft) model matches my experience in reality better - I have worked dickerman fine before, I am not able to hear kelly

## Questions
comparison to radio mobile?
what propagation models are there? are some known to work better in the mountains?
should I be adjusting the parameters in the .lrp file more?
what are the different propagation modes? others besides hoizon diffraction?
    - LOS, single, double
    - diffraction dom or troposcatter dom


## Other Tools
- NTIA Irregular Terrain Model (ITM) aka Longley-Rice Model
    - This is the standard model that most tools use various implementations of
    - [Example C++ github repo](https://github.com/NTIA/itm)
    - [Archived Fortran github repo](https://github.com/NTIA/itm-longley-rice)
    - Supported terrain resolutions: ?
- Radio Mobile
    - Not open-source, but free to use
    - Uses ITM, details here https://www.ve2dbe.com/data.html
    - [Windows download](https://www.ve2dbe.com/download/download.html)
    - [Online](https://www.ve2dbe.com/rmonline_s.asp)
    - Supported terrain resolutions: 90m/30m/10m/3m?
        - https://www.ve2dbe.com/dataen.html
        - ["The program can read GTOPO30, GLOBE and DTED level 0 at 30 arc second, SRTM and DTED level 1 at 3 arc second, DTED level 2 and SRTM at 1 arcsecond, and BIL at any resolution"](http://radiomobile.pe1mew.nl/?The_program___File_menu___Map_properties)
- [CloudRF](https://cloudrf.com/)
    - Not open-source, [free and paid plans](https://cloudrf.com/plans/)
    - [Calculation engine description](https://cloudrf.com/docs/sleipnir-propagation-engine)
    - Multi-resolution: "surface model data is fused to a seamless raster irrespective of resolution so you could drop 50cm drone photogrammetry from Pix4D onto 30m DSM"
    - Other models supported: HATA, COST/HATA, ECC33, EGLI, SUI, Ericsson9999
        - Does NOT contain ITWOM (GPL-licensed) so that it can be proprietary
- Signal Server
    - "This SPLAT! fork used to power CloudRF.com from 2012 to 2016 before it was replaced with a purpose built engine"
    - last archive.org capture of Cloud-RF version before removed from github: https://web.archive.org/web/20231118075249/https://github.com/Cloud-RF/Signal-Server
    - current fork https://github.com/lmux/signal-server
    - Supported terrain resolutions: ?
- [RF_Signals github repo](https://github.com/thebracket/rf-signals)
    - "a pure Rust port of Cloud-RF/Signal Server's algorithms. In turn, this is based upon SPLAT! by Alex Farrant and John A. Magliacane"
    - Supported terrain resolutions: ?
    - Other models supported: COST/HATA, HATA, ECC33, EGLI, ITWOM3, Plane Earth, SOIL, SUI
- Pathloss
    - Not open-source, [paid](https://www.pathloss.com/purchase.html)
    - [Some engine details described](https://www.pathloss.com/p5/docs/pl5_white_paper.pdf)
    - Supported terrain resolutions: 90m/30m/10m/3m?
        - https://www.pathloss.com/pathloss5.html

## Models
TODO - some are more relevant to UHF/cell networks/urba networks than my use case
TIREM? https://spectrum.hii-tsd.com/ModelStorefront/tirem?id=110
other listed https://www.pathloss.com/pathloss5.html
Deygout
Epstein-Peterson
HATA etc.



washington lattitude/longitude span:
- NW square is 48:49, -125:-124
- NE square is 48:49, -118:-117
- bottom row 46:47 ALMOST covers stuff, but we need 45:46 in some places
- that's an 8x4 grid, 32 squares
    - 40mb for .zip and .hgt
    - 50mb for .sdf
    - 90mb * 32 ~= 3gb to cover all of washington

SRTM grids are named by SW corner, so need:
- N48, W125 to W118
- N47, W125 to W118
- N46, W125 to W118
- N45, selected?

`for myfile in ./terrain/srtm1_v3/N48-49/*.hgt; do ./src/splat-1.4.2/utils/srtm2sdf-hd $myfile; done`

## Generate.py Usage ##
### Directory Format Before
```
.
├── generate.py
├── input
│   ├── apt.lrp
│   ├── apt.qth
│   └── W7W
│       ├── CH
│       ├── CW
│       ├── FR
│       ├── KG
│       ├── LC
│       ├── MC
│       ├── NO
│       ├── OK
│       ├── PL
│       ├── PO
│       ├── RS
│       ├── SK
│       ├── SN
│       ├── SO
│       ├── ST
│       ├── WE
│       └── WH
├── src
│   ├── splat-1.4.2
│   │   ├── ... (trimmed)
│   └── splat-1.4.2.tar.bz2
├── summitslist_W7W_25-08-21.csv
├── terrain
│   ├── sdf1
│   │   ├── 45:46:117:118-hd.sdf
│   │   ├── 45:46:118:119-hd.sdf
│   │   ├── 45:46:119:120-hd.sdf
│   │   ├── 45:46:120:121-hd.sdf
│   │   ├── 45:46:121:122-hd.sdf
│   │   ├── 45:46:122:123-hd.sdf
│   │   ├── 45:46:123:124-hd.sdf
│   │   ├── 45:46:124:125-hd.sdf
│   │   ├── 46:47:117:118-hd.sdf
│   │   ├── 46:47:118:119-hd.sdf
│   │   ├── 46:47:119:120-hd.sdf
│   │   ├── 46:47:120:121-hd.sdf
│   │   ├── 46:47:121:122-hd.sdf
│   │   ├── 46:47:122:123-hd.sdf
│   │   ├── 46:47:123:124-hd.sdf
│   │   ├── 46:47:124:125-hd.sdf
│   │   ├── 47:48:117:118-hd.sdf
│   │   ├── 47:48:118:119-hd.sdf
│   │   ├── 47:48:119:120-hd.sdf
│   │   ├── 47:48:120:121-hd.sdf
│   │   ├── 47:48:121:122-hd.sdf
│   │   ├── 47:48:122:123-hd.sdf
│   │   ├── 47:48:123:124-hd.sdf
│   │   ├── 47:48:124:125-hd.sdf
│   │   ├── 48:49:117:118-hd.sdf
│   │   ├── 48:49:118:119-hd.sdf
│   │   ├── 48:49:119:120-hd.sdf
│   │   ├── 48:49:120:121-hd.sdf
│   │   ├── 48:49:121:122-hd.sdf
│   │   ├── 48:49:122:123-hd.sdf
│   │   ├── 48:49:123:124-hd.sdf
│   │   └── 48:49:124:125-hd.sdf
└── W7W
    ├── CH
    ├── CW
    ├── FR
    ├── KG
    ├── LC
    ├── MC
    ├── NO
    ├── OK
    ├── PL
    ├── PO
    ├── RS
    ├── SK
    ├── SN
    ├── SO
    ├── ST
    ├── WE
    └── WH
```

### Invocation
`./generate.py ./summitslist_W7W_25-08-21.csv ./cw-prop.csv ./src/splat-1.4.2/splat-hd ./input/apt.qth ./input/ ./terrain/sdf1/ ./ -r CW`

### Directory Format After
```
.
├── apartment-site_report.txt
├── cw-prop.csv
├── generate.py
├── input
│   ├── apt.lrp
│   ├── apt.qth
│   └── W7W
│       ├── CH
│       ├── CW
│       │   ├── 001.qth
│       │   ├── 002.qth
│       │   ├── 003.qth
│       │   ├── 004.qth
│       │   ├── 005.qth
│       │   ├── ... (trimmed)
│       │   ├── 104.qth
│       │   ├── 105.qth
│       │   ├── 106.qth
│       │   ├── 107.qth
│       │   └── 108.qth
│       ├── FR
│       ├── KG
│       ├── LC
│       ├── MC
│       ├── NO
│       ├── OK
│       ├── PL
│       ├── PO
│       ├── RS
│       ├── SK
│       ├── SN
│       ├── SO
│       ├── ST
│       ├── WE
│       └── WH
├── src
│   ├── splat-1.4.2
│   │   ├── ... (trimmed)
│   └── splat-1.4.2.tar.bz2
├── summitslist_W7W_25-08-21.csv
├── terrain
│   ├── sdf1
│   │   ├── 45:46:117:118-hd.sdf
│   │   ├── 45:46:118:119-hd.sdf
│   │   ├── 45:46:119:120-hd.sdf
│   │   ├── 45:46:120:121-hd.sdf
│   │   ├── 45:46:121:122-hd.sdf
│   │   ├── 45:46:122:123-hd.sdf
│   │   ├── 45:46:123:124-hd.sdf
│   │   ├── 45:46:124:125-hd.sdf
│   │   ├── 46:47:117:118-hd.sdf
│   │   ├── 46:47:118:119-hd.sdf
│   │   ├── 46:47:119:120-hd.sdf
│   │   ├── 46:47:120:121-hd.sdf
│   │   ├── 46:47:121:122-hd.sdf
│   │   ├── 46:47:122:123-hd.sdf
│   │   ├── 46:47:123:124-hd.sdf
│   │   ├── 46:47:124:125-hd.sdf
│   │   ├── 47:48:117:118-hd.sdf
│   │   ├── 47:48:118:119-hd.sdf
│   │   ├── 47:48:119:120-hd.sdf
│   │   ├── 47:48:120:121-hd.sdf
│   │   ├── 47:48:121:122-hd.sdf
│   │   ├── 47:48:122:123-hd.sdf
│   │   ├── 47:48:123:124-hd.sdf
│   │   ├── 47:48:124:125-hd.sdf
│   │   ├── 48:49:117:118-hd.sdf
│   │   ├── 48:49:118:119-hd.sdf
│   │   ├── 48:49:119:120-hd.sdf
│   │   ├── 48:49:120:121-hd.sdf
│   │   ├── 48:49:121:122-hd.sdf
│   │   ├── 48:49:122:123-hd.sdf
│   │   ├── 48:49:123:124-hd.sdf
│   │   └── 48:49:124:125-hd.sdf
└── W7W
    ├── CH
    ├── CW
    │   ├── 001.png
    │   ├── 001.txt
    │   ├── 002.png
    │   ├── 002.txt
    │   ├── 003.png
    │   ├── 003.txt
    │   ├── 004.png
    │   ├── 004.txt
    │   ├── 005.png
    │   ├── 005.txt
    │   ├── ... (trimmed)
    │   ├── 104.png
    │   ├── 104.txt
    │   ├── 105.png
    │   ├── 105.txt
    │   ├── 106.png
    │   ├── 106.txt
    │   ├── 107.png
    │   ├── 107.txt
    │   ├── 108.png
    │   └── 108.txt
    ├── FR
    ├── KG
    ├── LC
    ├── MC
    ├── NO
    ├── OK
    ├── PL
    ├── PO
    ├── RS
    ├── SK
    ├── SN
    ├── SO
    ├── ST
    ├── WE
    └── WH
```

