# jpegli

`./dec.py jpegli ~/Pictures/gb82-image-set/png/*.png`

## fssimu2

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
djpegli | 84.877894 | 84.798063 | 88.677897 | 80.359648 | 2.647382
ffmpeg_filtered | 84.221104 | 84.176620 | 87.618734 | 80.826713 | 1.970696
imagemagick | 83.639452 | 83.591812 | 87.428527 | 80.008646 | 2.032487
ffmpeg_basic | 82.970937 | 82.922608 | 86.245012 | 79.328041 | 2.041009

## butteraugli

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 0.912447 | 0.903764 | 1.139952 | 0.774568 | 0.091585
djpegli | 0.934370 | 0.912149 | 1.476881 | 0.749394 | 0.172051
imagemagick | 0.963867 | 0.943705 | 1.464840 | 0.794021 | 0.164196
ffmpeg_basic | 1.243663 | 1.217537 | 1.730141 | 0.796687 | 0.179495

## fcvvdp

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 9.831656 | 9.831249 | 9.933700 | 9.696300 | 0.064401
imagemagick | 9.822804 | 9.822357 | 9.927600 | 9.676200 | 0.067453
ffmpeg_basic | 9.821652 | 9.821234 | 9.921700 | 9.686400 | 0.065257
djpegli | 9.814056 | 9.813503 | 9.926000 | 9.642800 | 0.075019

# libwebp (FFmpeg color conversion)

`./dec.py libwebp ~/Pictures/gb82-image-set/png/*.png`

## fssimu2

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 83.981282 | 83.926374 | 87.164804 | 80.422745 | 2.182956
dwebp | 83.482966 | 83.421160 | 86.798365 | 79.581865 | 2.306114
dwebp_nofancy | 83.468475 | 83.408314 | 86.619699 | 79.612493 | 2.274715
ffmpeg_basic | 81.793998 | 81.695696 | 86.112167 | 76.065414 | 2.875627

## butteraugli

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 0.940935 | 0.907668 | 1.205038 | 0.607083 | 0.171923
dwebp_nofancy | 0.976133 | 0.939316 | 1.372711 | 0.648714 | 0.188035
dwebp | 0.980940 | 0.938916 | 1.502618 | 0.659297 | 0.211980
ffmpeg_basic | 1.499752 | 1.427592 | 2.901626 | 0.821318 | 0.377068

## fcvvdp

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 9.829808 | 9.829081 | 9.935700 | 9.597400 | 0.085905
dwebp_nofancy | 9.825252 | 9.824534 | 9.933400 | 9.590700 | 0.085342
dwebp | 9.819532 | 9.818851 | 9.927300 | 9.591500 | 0.083160
ffmpeg_basic | 9.807320 | 9.806494 | 9.930700 | 9.557200 | 0.091502

# libwebp (Sharp YUV color conversion)

`./dec.py libwebp_sharpyuv ~/Pictures/gb82-image-set/png/*.png`

## fssimu2

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
dwebp | 84.362438 | 84.298126 | 87.823181 | 80.055187 | 2.366814
ffmpeg_filtered | 83.680428 | 83.627520 | 86.680586 | 79.264336 | 2.136388
dwebp_nofancy | 82.859014 | 82.783540 | 86.338575 | 75.651967 | 2.516715
ffmpeg_basic | 81.260756 | 81.160867 | 84.986670 | 74.942331 | 2.883897

## butteraugli

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
dwebp | 0.906762 | 0.874197 | 1.164410 | 0.555585 | 0.163387
ffmpeg_filtered | 0.984105 | 0.938590 | 1.631552 | 0.624721 | 0.225447
dwebp_nofancy | 1.033510 | 0.976824 | 1.800625 | 0.634622 | 0.261222
ffmpeg_basic | 1.512860 | 1.428249 | 3.104800 | 0.838822 | 0.418373

## fcvvdp

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
dwebp | 9.836200 | 9.835378 | 9.953100 | 9.587100 | 0.091366
ffmpeg_filtered | 9.827652 | 9.826932 | 9.939600 | 9.590400 | 0.085480
dwebp_nofancy | 9.826000 | 9.825267 | 9.945200 | 9.584800 | 0.086243
ffmpeg_basic | 9.809136 | 9.808271 | 9.942300 | 9.548800 | 0.093627

# libwebp (internal color conversion)

`./dec.py libwebp_default ~/Pictures/gb82-image-set/png/*.png`

## fssimu2

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 83.930835 | 83.873285 | 86.955767 | 80.416494 | 2.234440
dwebp_nofancy | 83.442849 | 83.380761 | 86.485961 | 79.469710 | 2.311306
dwebp | 83.381580 | 83.316132 | 86.668109 | 79.264292 | 2.373083
ffmpeg_basic | 81.821044 | 81.720057 | 85.896852 | 76.369292 | 2.915237

## butteraugli

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 0.932911 | 0.899850 | 1.213438 | 0.603410 | 0.171116
dwebp_nofancy | 0.969056 | 0.933168 | 1.373279 | 0.643980 | 0.186129
dwebp | 0.979749 | 0.938145 | 1.519840 | 0.651328 | 0.214743
ffmpeg_basic | 1.492239 | 1.421445 | 2.893639 | 0.827526 | 0.374481

## fcvvdp

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 9.828944 | 9.828234 | 9.934400 | 9.595200 | 0.084941
dwebp_nofancy | 9.824212 | 9.823508 | 9.932000 | 9.589000 | 0.084560
dwebp | 9.817856 | 9.817188 | 9.930200 | 9.589800 | 0.082362
ffmpeg_basic | 9.806324 | 9.805499 | 9.928500 | 9.555000 | 0.091445

# SVT-AV1

`./dec.py svtav1 ~/Pictures/gb82-image-set/png/*.png`

## fssimu2

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 82.871374 | 82.823967 | 86.816341 | 78.247238 | 2.014957
ffmpeg_basic | 82.700499 | 82.651174 | 86.528250 | 77.615689 | 2.049519
avifdec | 81.434026 | 81.386237 | 84.718092 | 76.043046 | 1.996439

## butteraugli

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 0.986756 | 0.976734 | 1.337789 | 0.839945 | 0.107110
ffmpeg_basic | 1.064154 | 1.049657 | 1.471589 | 0.863865 | 0.135081

## fcvvdp

Decoder | Avg | H-mean | max | min | stddev
-- | -- | -- | -- | -- | --
ffmpeg_filtered | 9.792080 | 9.791528 | 9.885000 | 9.580200 | 0.074712
ffmpeg_basic | 9.788044 | 9.787494 | 9.881500 | 9.580000 | 0.074554
avifdec | 9.769028 | 9.768392 | 9.872100 | 9.548700 | 0.080127
