echo "Running model analysis"
python3 analysis.py -m "./models/default.h5" -c "./conf/completivenessAnalysis.yaml" -p 0 -v 0

echo "Running model protection"
python3 protection.py -m "./models/default.h5" -c "./conf/completivenessAnalysis.yaml" -p 0 -i "./conf/completiveness_analysis_u0_l0.npy" -v 0