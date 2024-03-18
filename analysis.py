import ruamel.yaml
import argparse
import tensorflow as tf
from src import parameterProtection as prtct
import urllib.request
import os

def load_model(float_model_path):
    if not os.path.isfile(float_model_path):
        urllib.request.urlretrieve('https://gitlab.com/EHU-GDED/FLOSS/HSI-Drive/-/raw/wip/jon/ci/pycode/testing/pretrained_models/v2.0/example.h5?inline=false', './models/model.h5')
        trained_model = tf.keras.models.load_model('./models/model.h5', compile=False)
    else:
        trained_model = tf.keras.models.load_model(float_model_path, compile=False)
    return trained_model

def analysis(float_model_path, confFile, protectionLevel, verbose):

    #OUTPUT
    infoArray = "./conf/completiveness_analysis_u" + str(protectionLevel) + "_l" + str(protectionLevel) + ".npy"

    yaml = ruamel.yaml.YAML(typ='rt')
    with open(confFile, 'r') as fp:
        data = yaml.load(fp)
    fp.close()

    # Typical values for the upper threshold are: 1.999 (u0) / 1.99 (u1) / 1.95 (u2) / 1.9 (u3)
    upp_thr = [1.999, 1.99, 1.95, 1.9]
    # Typical values for the lower threshold are: 1.001 (l0) / 1.01 (l1) / 1.05 (l2) / 1.1 (l3)
    low_thr = [1.001, 1.01, 1.05, 1.1]

    with open(confFile, 'w') as fp:
        data['Action'] = 'completiveness_analysis'
        data['Upp_thr'] = upp_thr[protectionLevel]
        data['Low_thr'] = low_thr[protectionLevel]
        yaml.dump(data, fp)
    fp.close()

    trained_model = load_model(float_model_path)
    prtct.actions(model=trained_model, confFile=confFile, infoArray = infoArray, verbose=verbose)

def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('-m', '--model_path',         type=str, default="./models/example.h5", help="Path where the model is stored")
    ap.add_argument('-c', '--conf_file',          type=str, default="./conf/completivenessAnalysis.yaml", help="Path where completivenessAnalysis.yaml is stored.")
    ap.add_argument('-p', '--protection_level',   type=int, default=0, help="The protection level that is going to be applied.")
    ap.add_argument('-v', '--verbose',            type=int, default=0, help="Verboisity level with between 0 and 2.")
    args = ap.parse_args()

    analysis(args.model_path, args.conf_file, args.protection_level, args.verbose)

if __name__ ==  "__main__":
    main()